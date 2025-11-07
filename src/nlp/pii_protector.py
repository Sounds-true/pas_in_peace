"""PII detection and protection using Presidio and Natasha."""

from typing import List, Dict, Any, Optional
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
import re

from src.core.logger import get_logger


logger = get_logger(__name__)


class PIIProtector:
    """Protects PII using Presidio and Russian NER."""

    def __init__(self):
        """Initialize PII protector."""
        self.analyzer: Optional[AnalyzerEngine] = None
        self.anonymizer: Optional[AnonymizerEngine] = None
        self.supported_languages = ["en", "ru"]

        # Russian PII patterns
        self.russian_patterns = {
            "PHONE": r'\+?[78][\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}',
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "PASSPORT": r'\b[0-9]{4}\s?[0-9]{6}\b',
            "SNILS": r'\b[0-9]{3}-[0-9]{3}-[0-9]{3}\s?[0-9]{2}\b',
        }

    async def initialize(self) -> None:
        """Initialize Presidio engines."""
        try:
            # Configure NLP engine for multiple languages
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "en", "model_name": "en_core_web_sm"},
                    {"lang_code": "ru", "model_name": "ru_core_news_sm"}
                ]
            }

            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()

            # Create registry with custom recognizers
            registry = RecognizerRegistry()
            # Load predefined recognizers only for English (Presidio limitation)
            registry.load_predefined_recognizers(
                nlp_engine=nlp_engine,
                languages=["en"]
            )

            # Add custom Russian recognizers
            self._add_russian_recognizers(registry)

            # Initialize analyzer (supported languages inferred from registry and nlp_engine)
            self.analyzer = AnalyzerEngine(
                registry=registry,
                nlp_engine=nlp_engine
            )

            # Initialize anonymizer
            self.anonymizer = AnonymizerEngine()

            logger.info("pii_protector_initialized", languages=self.supported_languages)

        except Exception as e:
            logger.error("pii_protector_init_failed", error=str(e))
            # Continue without PII protection but log warning
            logger.warning("pii_protection_disabled")

    def _add_russian_recognizers(self, registry: RecognizerRegistry) -> None:
        """Add custom Russian PII recognizers."""
        from presidio_analyzer import Pattern, PatternRecognizer

        # Russian phone recognizer
        phone_recognizer = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            supported_language="ru",
            patterns=[Pattern("RUSSIAN_PHONE", self.russian_patterns["PHONE"], 0.7)]
        )
        registry.add_recognizer(phone_recognizer)

        # Russian passport recognizer
        passport_recognizer = PatternRecognizer(
            supported_entity="RU_PASSPORT",
            supported_language="ru",
            patterns=[Pattern("RUSSIAN_PASSPORT", self.russian_patterns["PASSPORT"], 0.8)]
        )
        registry.add_recognizer(passport_recognizer)

        # SNILS recognizer
        snils_recognizer = PatternRecognizer(
            supported_entity="RU_SNILS",
            supported_language="ru",
            patterns=[Pattern("RUSSIAN_SNILS", self.russian_patterns["SNILS"], 0.9)]
        )
        registry.add_recognizer(snils_recognizer)

    async def detect_pii(self, text: str, language: str = "ru") -> List[Dict[str, Any]]:
        """
        Detect PII in text.

        Args:
            text: Input text
            language: Language code (ru/en)

        Returns:
            List of detected PII entities
        """
        if not self.analyzer:
            logger.warning("pii_analyzer_not_initialized")
            return []

        try:
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=None,  # Detect all entity types
                return_decision_process=False
            )

            pii_entities = []
            for result in results:
                pii_entities.append({
                    "type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "text": text[result.start:result.end]
                })

            if pii_entities:
                logger.warning(
                    "pii_detected",
                    count=len(pii_entities),
                    types=[e["type"] for e in pii_entities]
                )

            return pii_entities

        except Exception as e:
            logger.error("pii_detection_failed", error=str(e))
            return []

    async def anonymize_text(
        self,
        text: str,
        language: str = "ru",
        anonymization_type: str = "replace"
    ) -> str:
        """
        Anonymize PII in text.

        Args:
            text: Input text
            language: Language code
            anonymization_type: Type of anonymization (replace/mask/redact)

        Returns:
            Anonymized text
        """
        if not self.analyzer or not self.anonymizer:
            logger.warning("pii_engines_not_initialized")
            return text

        try:
            # Detect PII
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=None
            )

            if not results:
                return text

            # Configure anonymization operators
            operators = {}
            if anonymization_type == "replace":
                operators = {
                    "PERSON": OperatorConfig("replace", {"new_value": "[ИМЯ]"}),
                    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[ТЕЛЕФОН]"}),
                    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
                    "LOCATION": OperatorConfig("replace", {"new_value": "[АДРЕС]"}),
                    "RU_PASSPORT": OperatorConfig("replace", {"new_value": "[ПАСПОРТ]"}),
                    "RU_SNILS": OperatorConfig("replace", {"new_value": "[СНИЛС]"}),
                    "DEFAULT": OperatorConfig("replace", {"new_value": "[УДАЛЕНО]"})
                }
            elif anonymization_type == "mask":
                operators = {
                    "DEFAULT": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 100})
                }
            else:  # redact
                operators = {
                    "DEFAULT": OperatorConfig("redact", {})
                }

            # Anonymize
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators
            )

            logger.info("text_anonymized", original_length=len(text), anonymized_length=len(anonymized_result.text))

            return anonymized_result.text

        except Exception as e:
            logger.error("anonymization_failed", error=str(e))
            return text

    async def check_safe_for_logging(self, text: str) -> bool:
        """
        Check if text is safe for logging (contains no PII).

        Args:
            text: Text to check

        Returns:
            True if safe, False if contains PII
        """
        pii_entities = await self.detect_pii(text)
        return len(pii_entities) == 0

    async def get_safe_text_for_logging(self, text: str, language: str = "ru") -> str:
        """
        Get PII-free version of text for logging.

        Args:
            text: Original text
            language: Language code

        Returns:
            Anonymized text safe for logging
        """
        return await self.anonymize_text(text, language, anonymization_type="replace")