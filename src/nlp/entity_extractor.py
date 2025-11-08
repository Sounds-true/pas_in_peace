"""Entity extraction for PA context using Natasha."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

try:
    from natasha import (
        Segmenter,
        NewsEmbedding,
        NewsMorphTagger,
        NewsNERTagger,
        Doc
    )
    NATASHA_AVAILABLE = True
except ImportError:
    NATASHA_AVAILABLE = False

from src.core.logger import get_logger


logger = get_logger(__name__)


@dataclass
class Entity:
    """Extracted entity."""
    type: str  # 'person', 'date', 'relationship', 'location', 'organization'
    value: str
    normalized: Optional[str] = None
    confidence: float = 1.0


@dataclass
class ExtractedContext:
    """Extracted context from user message."""
    entities: List[Entity]
    child_names: List[str]
    ex_partner_name: Optional[str] = None
    court_date: Optional[datetime] = None
    relationships: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    organizations: List[str] = field(default_factory=list)


class EntityExtractor:
    """Extract entities from Russian text for PA context."""

    def __init__(self):
        """Initialize entity extractor."""
        self.initialized = False
        self.segmenter = None
        self.embedding = None
        self.morph_tagger = None
        self.ner_tagger = None

        # PA-specific patterns
        self.relationship_patterns = [
            r'моя?\s+(?:бывша[яе]|экс)?\s*жена',
            r'моя?\s+(?:бывш[ие]й|экс)?\s*муж',
            r'моя?\s+дочь|моя?\s+сын',
            r'наш[аие]?\s+дет[ие]',
            r'ребёнок|ребенок',
            r'мать|отец',
            r'родител[ьи]',
        ]

        # Court/legal patterns
        self.date_patterns = [
            r'(\d{1,2})\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)(?:\s+(\d{4}))?',
            r'(\d{1,2})[\./-](\d{1,2})[\./-](\d{2,4})',
            r'через\s+(\d+)\s+(?:день|дня|дней|недел[юи]|месяц[ае]?)',
            r'до\s+(\d{1,2})\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)',
        ]

    async def initialize(self) -> bool:
        """Initialize Natasha models with timeout protection."""
        if self.initialized:
            return True

        if not NATASHA_AVAILABLE:
            logger.warning("natasha_not_available",
                          message="Entity extraction will use fallback patterns")
            self.initialized = True
            return False

        try:
            # Add timeout to prevent hanging
            import asyncio
            from concurrent.futures import ThreadPoolExecutor

            def _init_natasha():
                """Initialize Natasha components (sync)."""
                self.segmenter = Segmenter()
                self.embedding = NewsEmbedding()
                self.morph_tagger = NewsMorphTagger(self.embedding)
                self.ner_tagger = NewsNERTagger(self.embedding)

            # Run in executor with 10 second timeout
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            await asyncio.wait_for(
                loop.run_in_executor(executor, _init_natasha),
                timeout=10.0
            )

            self.initialized = True
            logger.info("entity_extractor_initialized", backend="natasha")
            return True

        except asyncio.TimeoutError:
            logger.warning("entity_extractor_init_timeout",
                          message="Natasha initialization timed out, using pattern fallback")
            self.initialized = True  # Mark as initialized to use fallback
            return False
        except Exception as e:
            logger.error("entity_extractor_init_failed", error=str(e))
            self.initialized = True  # Mark as initialized to use fallback
            return False

    async def extract(self, text: str, user_context: Optional[Dict[str, Any]] = None) -> ExtractedContext:
        """
        Extract entities from text.

        Args:
            text: User message
            user_context: Previous user context (for entity resolution)

        Returns:
            ExtractedContext with all extracted entities
        """
        if not self.initialized:
            await self.initialize()

        entities = []

        # Try Natasha NER first
        if self.ner_tagger:
            entities.extend(await self._natasha_extract(text))

        # Fallback to pattern matching (always run for PA-specific entities)
        entities.extend(await self._pattern_extract(text))

        # Resolve and structure entities
        context = await self._resolve_context(entities, user_context)

        return context

    async def _natasha_extract(self, text: str) -> List[Entity]:
        """Extract entities using Natasha NER."""
        entities = []

        try:
            doc = Doc(text)
            doc.segment(self.segmenter)
            doc.tag_morph(self.morph_tagger)
            doc.tag_ner(self.ner_tagger)

            for span in doc.spans:
                entity_type = self._map_natasha_type(span.type)
                entities.append(Entity(
                    type=entity_type,
                    value=span.text,
                    normalized=span.normal if hasattr(span, 'normal') else None,
                    confidence=0.9
                ))

        except Exception as e:
            logger.warning("natasha_extraction_failed", error=str(e))

        return entities

    async def _pattern_extract(self, text: str) -> List[Entity]:
        """Extract PA-specific entities using patterns."""
        entities = []

        # Extract relationships
        for pattern in self.relationship_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    type='relationship',
                    value=match.group(0),
                    confidence=0.8
                ))

        # Extract dates
        for pattern in self.date_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    type='date',
                    value=match.group(0),
                    confidence=0.7
                ))

        # Extract potential names (capitalized words not at sentence start)
        name_pattern = r'(?<!^)(?<![.!?]\s)([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)'
        for match in re.finditer(name_pattern, text):
            # Skip common words
            name = match.group(1)
            if len(name) > 3 and not self._is_common_word(name):
                entities.append(Entity(
                    type='person',
                    value=name,
                    confidence=0.6
                ))

        return entities

    async def _resolve_context(
        self,
        entities: List[Entity],
        user_context: Optional[Dict[str, Any]]
    ) -> ExtractedContext:
        """Resolve entities into structured context."""
        child_names = []
        ex_partner_name = None
        court_date = None
        relationships = []
        locations = []
        organizations = []

        # Group by type
        for entity in entities:
            if entity.type == 'person':
                # Heuristic: first person mentioned might be child or ex-partner
                # Context from previous messages helps
                if user_context and 'child_name' in user_context:
                    if entity.value.lower() in user_context['child_name'].lower():
                        child_names.append(entity.value)
                else:
                    child_names.append(entity.value)

            elif entity.type == 'relationship':
                relationships.append(entity.value)

            elif entity.type == 'date':
                # Parse date if needed
                court_date = entity.value  # Simplified, would parse to datetime

            elif entity.type == 'location':
                locations.append(entity.value)

            elif entity.type == 'organization':
                organizations.append(entity.value)

        return ExtractedContext(
            entities=entities,
            child_names=list(set(child_names)),  # Deduplicate
            ex_partner_name=ex_partner_name,
            court_date=court_date,
            relationships=relationships,
            locations=locations,
            organizations=organizations
        )

    def _map_natasha_type(self, natasha_type: str) -> str:
        """Map Natasha entity types to our types."""
        mapping = {
            'PER': 'person',
            'LOC': 'location',
            'ORG': 'organization',
        }
        return mapping.get(natasha_type, 'other')

    def _is_common_word(self, word: str) -> bool:
        """Check if word is too common to be a name."""
        common_words = {
            'Сегодня', 'Вчера', 'Завтра', 'Когда', 'Почему',
            'Как', 'Что', 'Где', 'Кто', 'Спасибо', 'Пожалуйста'
        }
        return word in common_words

    async def update_user_context(
        self,
        user_id: str,
        extracted: ExtractedContext,
        existing_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user context with newly extracted entities.

        Merges with existing context intelligently.
        """
        updated = existing_context.copy()

        # Add child names (accumulate)
        if extracted.child_names:
            existing_children = updated.get('child_names', [])
            updated['child_names'] = list(set(existing_children + extracted.child_names))

        # Update ex-partner if more confident
        if extracted.ex_partner_name:
            updated['ex_partner_name'] = extracted.ex_partner_name

        # Update court date if present
        if extracted.court_date:
            updated['court_date'] = extracted.court_date

        # Accumulate relationships mentioned
        if extracted.relationships:
            existing_rels = updated.get('relationships', [])
            updated['relationships'] = list(set(existing_rels + extracted.relationships))

        logger.info("user_context_updated",
                   user_id=user_id,
                   child_names=updated.get('child_names', []),
                   relationships=len(updated.get('relationships', [])))

        return updated


# Import for dataclass field
from dataclasses import field
