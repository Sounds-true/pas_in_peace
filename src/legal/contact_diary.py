"""
Contact Diary Module - Court-Admissible Documentation System

This module provides a structured system for parents to document interactions
with their children in a neutral, factual manner that can be used as evidence
in family court proceedings.

Legal Framework:
- Follows best practices for family law documentation
- Neutral, factual language only (no interpretations or emotions)
- Timestamped entries with immutable history
- Structured format suitable for legal review

Author: pas_in_peace
License: MIT
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from dataclasses import dataclass, asdict
import hashlib


class ContactType(Enum):
    """Types of contact with child"""
    IN_PERSON = "in_person"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    TEXT_MESSAGE = "text_message"
    MISSED_VISIT = "missed_visit"
    LATE_PICKUP = "late_pickup"
    EARLY_RETURN = "early_return"
    OTHER = "other"


class EntryCategory(Enum):
    """Categories for diary entries"""
    POSITIVE_INTERACTION = "positive_interaction"
    NEUTRAL_OBSERVATION = "neutral_observation"
    CONCERNING_BEHAVIOR = "concerning_behavior"
    COMMUNICATION_ISSUE = "communication_issue"
    SCHEDULE_ADHERENCE = "schedule_adherence"
    CHILD_WELLBEING = "child_wellbeing"
    OTHER = "other"


@dataclass
class ContactEntry:
    """Single contact diary entry - court-admissible format"""

    entry_id: str
    timestamp: str  # ISO 8601 format
    contact_type: ContactType
    category: EntryCategory

    # Core factual information
    date_of_contact: str  # YYYY-MM-DD
    time_of_contact: str  # HH:MM
    duration_minutes: Optional[int]
    location: str

    # Participants
    child_name: str  # Initials only for privacy
    other_parent_present: bool
    other_adults_present: List[str]  # Initials or roles

    # Factual observations (neutral language only)
    observations: str  # What happened (factual, no interpretation)
    child_statements: List[str]  # Direct quotes from child
    child_behavior: str  # Observable behaviors only

    # Context
    scheduled_vs_actual: Dict[str, Any]  # Planned vs actual time/duration
    documentation: List[str]  # References to photos, texts, etc.

    # Metadata
    created_by: str
    checksum: str  # For tamper detection


class ContactDiary:
    """
    Court-Admissible Contact Diary System

    Provides parents with a structured way to document interactions with
    their children in family law contexts. Emphasizes:
    - Factual, neutral language
    - Timestamped, immutable entries
    - Structured format for legal review
    - Privacy protection (initials, no full names)
    """

    def __init__(self, parent_id: str):
        """
        Initialize contact diary for a parent

        Args:
            parent_id: Anonymized parent identifier
        """
        self.parent_id = parent_id
        self.entries: List[ContactEntry] = []

    def create_entry(
        self,
        contact_type: ContactType,
        category: EntryCategory,
        date_of_contact: str,
        time_of_contact: str,
        duration_minutes: Optional[int],
        location: str,
        child_name: str,
        observations: str,
        child_statements: Optional[List[str]] = None,
        child_behavior: Optional[str] = None,
        other_parent_present: bool = False,
        other_adults_present: Optional[List[str]] = None,
        scheduled_vs_actual: Optional[Dict[str, Any]] = None,
        documentation: Optional[List[str]] = None
    ) -> ContactEntry:
        """
        Create a new contact diary entry with validation

        Args:
            contact_type: Type of contact (in-person, phone, etc.)
            category: Category of entry
            date_of_contact: Date in YYYY-MM-DD format
            time_of_contact: Time in HH:MM format
            duration_minutes: Duration of contact
            location: Location of contact
            child_name: Child's initials (e.g., "J.S.")
            observations: Factual observations (neutral language)
            child_statements: Direct quotes from child
            child_behavior: Observable behaviors only
            other_parent_present: Whether other parent was present
            other_adults_present: List of other adults (initials/roles)
            scheduled_vs_actual: Comparison of planned vs actual
            documentation: References to supporting documents

        Returns:
            ContactEntry object
        """
        # Validate neutral language
        self._validate_neutral_language(observations)
        if child_behavior:
            self._validate_neutral_language(child_behavior)

        # Generate entry ID and checksum
        entry_id = self._generate_entry_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        entry_data = {
            "entry_id": entry_id,
            "timestamp": timestamp,
            "contact_type": contact_type.value,
            "category": category.value,
            "date_of_contact": date_of_contact,
            "time_of_contact": time_of_contact,
            "duration_minutes": duration_minutes,
            "location": location,
            "child_name": child_name,
            "other_parent_present": other_parent_present,
            "other_adults_present": other_adults_present or [],
            "observations": observations,
            "child_statements": child_statements or [],
            "child_behavior": child_behavior or "",
            "scheduled_vs_actual": scheduled_vs_actual or {},
            "documentation": documentation or [],
            "created_by": self.parent_id
        }

        checksum = self._generate_checksum(entry_data)
        entry_data["checksum"] = checksum

        entry = ContactEntry(**entry_data)
        self.entries.append(entry)

        return entry

    def _validate_neutral_language(self, text: str) -> None:
        """
        Validate that text uses neutral, factual language

        Warns if emotional or interpretive language detected

        Args:
            text: Text to validate
        """
        # Red flag words that indicate interpretation rather than observation
        interpretive_words = [
            "я думаю", "я чувствую", "казалось", "вероятно",
            "очевидно", "ясно что", "похоже", "наверное",
            "he seemed", "she appeared", "obviously", "clearly",
            "I think", "I feel", "probably", "likely"
        ]

        # Emotional language that should be avoided
        emotional_words = [
            "ужасный", "отвратительный", "замечательный", "прекрасный",
            "terrible", "horrible", "wonderful", "amazing",
            "плохой", "хороший", "bad", "good"
        ]

        text_lower = text.lower()

        found_issues = []
        for word in interpretive_words:
            if word in text_lower:
                found_issues.append(f"Interpretive language: '{word}'")

        for word in emotional_words:
            if word in text_lower:
                found_issues.append(f"Emotional language: '{word}'")

        if found_issues:
            # Log warning but don't block entry
            print(f"⚠️  Language validation warning: {', '.join(found_issues)}")
            print("   Consider rephrasing with factual, observable terms.")

    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(
            f"{self.parent_id}_{timestamp}_{len(self.entries)}".encode()
        ).hexdigest()[:16]

    def _generate_checksum(self, entry_data: Dict[str, Any]) -> str:
        """Generate checksum for tamper detection"""
        data_str = json.dumps(entry_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def get_entry(self, entry_id: str) -> Optional[ContactEntry]:
        """Retrieve entry by ID"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def get_entries_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[ContactEntry]:
        """
        Get entries within date range

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            List of entries in date range
        """
        return [
            entry for entry in self.entries
            if start_date <= entry.date_of_contact <= end_date
        ]

    def get_entries_by_category(
        self,
        category: EntryCategory
    ) -> List[ContactEntry]:
        """Get entries by category"""
        return [
            entry for entry in self.entries
            if entry.category == category
        ]

    def export_to_court_format(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """
        Export entries to court-formatted document

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Formatted text suitable for legal submission
        """
        entries = self.entries

        if start_date and end_date:
            entries = self.get_entries_by_date_range(start_date, end_date)

        # Sort by date and time
        entries.sort(key=lambda e: (e.date_of_contact, e.time_of_contact))

        output = []
        output.append("=" * 80)
        output.append("CONTACT DIARY - COURT SUBMISSION FORMAT")
        output.append("=" * 80)
        output.append(f"Parent ID: {self.parent_id}")
        output.append(f"Date Range: {start_date or 'All'} to {end_date or 'All'}")
        output.append(f"Total Entries: {len(entries)}")
        output.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        output.append("=" * 80)
        output.append("")

        for i, entry in enumerate(entries, 1):
            output.append(f"ENTRY #{i}")
            output.append("-" * 80)
            output.append(f"Entry ID: {entry.entry_id}")
            output.append(f"Date of Contact: {entry.date_of_contact}")
            output.append(f"Time of Contact: {entry.time_of_contact}")

            if entry.duration_minutes:
                output.append(f"Duration: {entry.duration_minutes} minutes")

            output.append(f"Contact Type: {entry.contact_type.value.replace('_', ' ').title()}")
            output.append(f"Category: {entry.category.value.replace('_', ' ').title()}")
            output.append(f"Location: {entry.location}")
            output.append(f"Child: {entry.child_name}")
            output.append(f"Other Parent Present: {'Yes' if entry.other_parent_present else 'No'}")

            if entry.other_adults_present:
                output.append(f"Other Adults Present: {', '.join(entry.other_adults_present)}")

            output.append("")
            output.append("OBSERVATIONS:")
            output.append(entry.observations)

            if entry.child_statements:
                output.append("")
                output.append("CHILD'S STATEMENTS (direct quotes):")
                for statement in entry.child_statements:
                    output.append(f'  - "{statement}"')

            if entry.child_behavior:
                output.append("")
                output.append("CHILD'S BEHAVIOR (observable):")
                output.append(entry.child_behavior)

            if entry.scheduled_vs_actual:
                output.append("")
                output.append("SCHEDULE ADHERENCE:")
                for key, value in entry.scheduled_vs_actual.items():
                    output.append(f"  {key}: {value}")

            if entry.documentation:
                output.append("")
                output.append("SUPPORTING DOCUMENTATION:")
                for doc in entry.documentation:
                    output.append(f"  - {doc}")

            output.append("")
            output.append(f"Entry Created: {entry.timestamp}")
            output.append(f"Checksum: {entry.checksum}")
            output.append("")
            output.append("")

        output.append("=" * 80)
        output.append("END OF CONTACT DIARY")
        output.append("=" * 80)

        return "\n".join(output)

    def generate_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics for the diary

        Returns:
            Dictionary with statistics
        """
        if not self.entries:
            return {
                "total_entries": 0,
                "date_range": None,
                "contact_types": {},
                "categories": {},
                "total_contact_time_minutes": 0,
                "missed_visits": 0,
                "late_pickups": 0
            }

        contact_types = {}
        categories = {}
        total_minutes = 0
        missed_visits = 0
        late_pickups = 0

        for entry in self.entries:
            # Count contact types
            ct = entry.contact_type.value
            contact_types[ct] = contact_types.get(ct, 0) + 1

            # Count categories
            cat = entry.category.value
            categories[cat] = categories.get(cat, 0) + 1

            # Sum contact time
            if entry.duration_minutes:
                total_minutes += entry.duration_minutes

            # Count specific issues
            if entry.contact_type == ContactType.MISSED_VISIT:
                missed_visits += 1
            elif entry.contact_type == ContactType.LATE_PICKUP:
                late_pickups += 1

        dates = [entry.date_of_contact for entry in self.entries]

        return {
            "total_entries": len(self.entries),
            "date_range": {
                "start": min(dates),
                "end": max(dates)
            },
            "contact_types": contact_types,
            "categories": categories,
            "total_contact_time_minutes": total_minutes,
            "total_contact_time_hours": round(total_minutes / 60, 1),
            "missed_visits": missed_visits,
            "late_pickups": late_pickups
        }

    def save_to_file(self, filepath: str) -> None:
        """
        Save diary to JSON file

        Args:
            filepath: Path to save file
        """
        data = {
            "parent_id": self.parent_id,
            "entries": [asdict(entry) for entry in self.entries],
            "metadata": {
                "created": datetime.utcnow().isoformat() + "Z",
                "version": "1.0"
            }
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, filepath: str) -> 'ContactDiary':
        """
        Load diary from JSON file

        Args:
            filepath: Path to load from

        Returns:
            ContactDiary instance
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        diary = cls(data["parent_id"])

        for entry_data in data["entries"]:
            # Convert strings back to enums
            entry_data["contact_type"] = ContactType(entry_data["contact_type"])
            entry_data["category"] = EntryCategory(entry_data["category"])

            entry = ContactEntry(**entry_data)
            diary.entries.append(entry)

        return diary


class ContactDiaryAssistant:
    """
    AI Assistant for helping parents create court-admissible diary entries

    Helps transform emotional or interpretive language into neutral,
    factual observations suitable for legal documentation.
    """

    @staticmethod
    def suggest_neutral_reframe(emotional_text: str) -> str:
        """
        Suggest neutral reframing of emotional/interpretive text

        Args:
            emotional_text: Original text with emotional language

        Returns:
            Suggested neutral reframe
        """
        # Common patterns to reframe
        reframes = {
            "он был счастлив": "он улыбался и смеялся",
            "она была грустной": "она плакала/была тихой",
            "он злился": "он повышал голос и размахивал руками",
            "она испугалась": "она отступила и говорила тихо",
            "хорошо провели время": "ребенок улыбался и участвовал в активностях",
            "плохо себя вел": "ребенок [specific behavior: кричал/отказывался слушаться]",
            "he was happy": "he smiled and laughed",
            "she was sad": "she cried/was quiet",
            "he was angry": "he raised his voice and gestured",
            "she was scared": "she stepped back and spoke quietly",
            "had a good time": "child smiled and participated in activities",
            "behaved badly": "child [specific behavior: yelled/refused to listen]"
        }

        suggestion = emotional_text
        for emotional, neutral in reframes.items():
            if emotional in emotional_text.lower():
                suggestion = suggestion.lower().replace(emotional, neutral)

        return suggestion

    @staticmethod
    def extract_facts_from_narrative(narrative: str) -> Dict[str, str]:
        """
        Help extract factual elements from a parent's narrative

        Args:
            narrative: Parent's original narrative

        Returns:
            Dictionary with structured factual elements
        """
        # This is a template - in production would use NLP
        return {
            "observations": "Extract observable facts here",
            "child_statements": "Extract direct quotes here",
            "child_behavior": "Extract observable behaviors here",
            "suggestion": "Focus on what you saw and heard, not what you think it means"
        }

    @staticmethod
    def provide_documentation_tips() -> List[str]:
        """Provide tips for effective diary documentation"""
        return [
            "✓ Use specific dates, times, and durations",
            "✓ Record direct quotes from your child in quotation marks",
            "✓ Describe observable behaviors (smiled, cried, yelled)",
            "✓ Avoid interpretations (don't say 'he was manipulating')",
            "✓ Stay neutral (avoid words like 'terrible', 'wonderful')",
            "✓ Include context (location, who was present)",
            "✓ Document schedule deviations (late pickups, missed visits)",
            "✓ Reference supporting evidence (photos, texts, witnesses)",
            "✓ Write entries soon after events for accuracy",
            "✓ Don't alter entries after creation (make new entries instead)"
        ]


# Example usage and templates
EXAMPLE_ENTRIES = {
    "positive_visit": {
        "contact_type": ContactType.IN_PERSON,
        "category": EntryCategory.POSITIVE_INTERACTION,
        "observations": (
            "Провел с ребенком 3 часа в парке. "
            "Ребенок активно участвовал в игре на детской площадке. "
            "Мы вместе обедали, ребенок съел весь обед."
        ),
        "child_statements": [
            "Папа, мне нравится когда мы вместе!",
            "Можно мы еще придем сюда?"
        ],
        "child_behavior": "Ребенок улыбался, смеялся, поддерживал физический контакт (держал за руку)"
    },

    "missed_visit": {
        "contact_type": ContactType.MISSED_VISIT,
        "category": EntryCategory.SCHEDULE_ADHERENCE,
        "observations": (
            "Запланированная встреча 14:00-17:00 не состоялась. "
            "Прибыл в согласованное место (адрес дома другого родителя) в 13:55. "
            "Позвонил в дверь, никто не ответил. "
            "Звонил на телефон другого родителя в 14:00, 14:15, 14:30 - не взяла трубку."
        ),
        "documentation": [
            "Фото входной двери с timestamp",
            "Скриншоты попыток звонков",
            "Текстовое сообщение отправленное в 14:35"
        ]
    }
}
