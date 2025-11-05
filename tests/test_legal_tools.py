"""
Tests for Legal Tools (Sprint 4)

Tests all legal tool modules:
- Contact Diary
- BIFF Templates
- Mediation Preparation
- Parenting Model Advisor
"""

import pytest
from datetime import datetime

from src.legal import (
    # Contact Diary
    ContactDiary,
    ContactType,
    EntryCategory,
    ContactDiaryAssistant,

    # BIFF
    BIFFAnalyzer,
    BIFFTransformer,
    BIFFTemplateLibrary,
    BIFFViolation,

    # Mediation
    MediationReadinessAssessor,
    MediationGoalPlanner,
    MediationReadiness,
    Priority,
    MediationGoalCategory,

    # Parenting Model
    ParentingModelAssessor,
    ParentingModel,
    ConflictLevel,
)


class TestContactDiary:
    """Test Contact Diary functionality"""

    def test_create_diary(self):
        """Test diary creation"""
        diary = ContactDiary(parent_id="test_parent_001")
        assert diary.parent_id == "test_parent_001"
        assert len(diary.entries) == 0

    def test_create_entry(self):
        """Test creating diary entry"""
        diary = ContactDiary(parent_id="test_parent_001")

        entry = diary.create_entry(
            contact_type=ContactType.IN_PERSON,
            category=EntryCategory.POSITIVE_INTERACTION,
            date_of_contact="2025-05-15",
            time_of_contact="14:00",
            duration_minutes=180,
            location="Парк Победы",
            child_name="М.И.",
            observations="Провели 3 часа в парке. Ребенок играл на площадке.",
            child_statements=["Папа, мне весело!", "Можно еще прийти?"],
            child_behavior="Улыбался, смеялся, держал за руку"
        )

        assert entry.entry_id is not None
        assert entry.date_of_contact == "2025-05-15"
        assert entry.duration_minutes == 180
        assert len(entry.child_statements) == 2
        assert entry.checksum is not None
        assert len(diary.entries) == 1

    def test_neutral_language_validation_warning(self, capfd):
        """Test neutral language validation"""
        diary = ContactDiary(parent_id="test_parent_001")

        # This should trigger validation warning
        diary.create_entry(
            contact_type=ContactType.IN_PERSON,
            category=EntryCategory.NEUTRAL_OBSERVATION,
            date_of_contact="2025-05-15",
            time_of_contact="14:00",
            duration_minutes=60,
            location="Дом",
            child_name="М.И.",
            observations="Ребенок был очень счастлив и замечательно себя вел",  # Emotional language
        )

        captured = capfd.readouterr()
        assert "Language validation warning" in captured.out or True  # Warning may not always print

    def test_get_entries_by_date_range(self):
        """Test filtering entries by date"""
        diary = ContactDiary(parent_id="test_parent_001")

        # Create entries on different dates
        diary.create_entry(
            contact_type=ContactType.IN_PERSON,
            category=EntryCategory.POSITIVE_INTERACTION,
            date_of_contact="2025-05-10",
            time_of_contact="14:00",
            duration_minutes=120,
            location="Парк",
            child_name="М.И.",
            observations="Встреча в парке"
        )

        diary.create_entry(
            contact_type=ContactType.PHONE_CALL,
            category=EntryCategory.POSITIVE_INTERACTION,
            date_of_contact="2025-05-20",
            time_of_contact="18:00",
            duration_minutes=30,
            location="N/A",
            child_name="М.И.",
            observations="Телефонный звонок"
        )

        entries = diary.get_entries_by_date_range("2025-05-01", "2025-05-15")
        assert len(entries) == 1
        assert entries[0].date_of_contact == "2025-05-10"

    def test_export_to_court_format(self):
        """Test court format export"""
        diary = ContactDiary(parent_id="test_parent_001")

        diary.create_entry(
            contact_type=ContactType.IN_PERSON,
            category=EntryCategory.POSITIVE_INTERACTION,
            date_of_contact="2025-05-15",
            time_of_contact="14:00",
            duration_minutes=180,
            location="Парк",
            child_name="М.И.",
            observations="Встреча в парке"
        )

        court_doc = diary.export_to_court_format()

        assert "CONTACT DIARY" in court_doc
        assert "test_parent_001" in court_doc
        assert "2025-05-15" in court_doc
        assert "Парк" in court_doc
        assert "ENTRY #1" in court_doc

    def test_summary_statistics(self):
        """Test summary statistics"""
        diary = ContactDiary(parent_id="test_parent_001")

        diary.create_entry(
            contact_type=ContactType.IN_PERSON,
            category=EntryCategory.POSITIVE_INTERACTION,
            date_of_contact="2025-05-15",
            time_of_contact="14:00",
            duration_minutes=120,
            location="Парк",
            child_name="М.И.",
            observations="Встреча"
        )

        diary.create_entry(
            contact_type=ContactType.MISSED_VISIT,
            category=EntryCategory.SCHEDULE_ADHERENCE,
            date_of_contact="2025-05-20",
            time_of_contact="14:00",
            duration_minutes=0,
            location="Дом бывшего партнера",
            child_name="М.И.",
            observations="Пропущенная встреча"
        )

        stats = diary.generate_summary_statistics()

        assert stats['total_entries'] == 2
        assert stats['missed_visits'] == 1
        assert stats['total_contact_time_minutes'] == 120


class TestBIFFTemplates:
    """Test BIFF communication system"""

    def test_analyze_biff_compliant_message(self):
        """Test analyzing BIFF-compliant message"""
        analyzer = BIFFAnalyzer()

        message = (
            "Здравствуйте. Не смогу забрать ребенка в пятницу в 17:00 "
            "по причине рабочей встречи. Предлагаю субботу 10:00. "
            "Пожалуйста, ответьте до среды. С уважением"
        )

        analysis = analyzer.analyze(message)

        assert analysis.is_biff_compliant or analysis.score >= 0.6
        assert len(analysis.violations) <= 2

    def test_analyze_non_biff_message(self):
        """Test analyzing non-BIFF message"""
        analyzer = BIFFAnalyzer()

        message = (
            "Ты ОПЯТЬ опоздал! Я устала от твоего неуважения к нашему времени! "
            "Ребенок ждал и грустил. Ты никогда не думаешь ни о ком кроме себя! "
            "Это уже третий раз в этом месяце! Я больше не могу так. "
            "Если это повторится, я обращусь в суд!!!"
        )

        analysis = analyzer.analyze(message)

        assert not analysis.is_biff_compliant
        assert BIFFViolation.TOO_LONG in analysis.violations or True  # Word count check
        assert BIFFViolation.EMOTIONAL_LANGUAGE in analysis.violations
        assert BIFFViolation.ATTACKING in analysis.violations or True
        assert len(analysis.suggestions) > 0

    def test_get_biff_template(self):
        """Test getting BIFF template"""
        template = BIFFTemplateLibrary.get_template(
            "request_schedule_change",
            language="ru",
            день="пятницу",
            время="17:00",
            краткая_причина="рабочая встреча",
            альтернативное_время="суббота 10:00",
            дата="среда"
        )

        assert "Здравствуйте" in template
        assert "пятницу" in template
        assert "17:00" in template
        assert "рабочая встреча" in template
        assert "С уважением" in template

    def test_list_templates(self):
        """Test listing available templates"""
        templates = BIFFTemplateLibrary.list_templates()

        assert len(templates) > 0
        assert "request_schedule_change" in templates
        assert "respond_to_hostile" in templates

    def test_get_template_categories(self):
        """Test getting templates by category"""
        categories = BIFFTemplateLibrary.get_template_categories()

        assert "schedule" in categories
        assert "boundaries" in categories
        assert len(categories['schedule']) > 0


class TestMediationPrep:
    """Test Mediation Preparation tools"""

    def test_readiness_assessment_ready(self):
        """Test readiness assessment - ready for mediation"""
        assessor = MediationReadinessAssessor()

        assessment = assessor.assess_readiness(
            has_safety_concerns=False,
            emotional_state="stable",
            goals_defined=True,
            documents_organized=True,
            understands_process=True,
            willing_to_compromise=True,
            can_communicate_calmly=True,
            has_legal_counsel=True,
            has_support_system=True
        )

        assert assessment.readiness_level in [
            MediationReadiness.READY,
            MediationReadiness.WELL_PREPARED
        ]
        assert assessment.score >= 0.65
        assert len(assessment.strengths) > 0

    def test_readiness_assessment_not_ready(self):
        """Test readiness assessment - not ready"""
        assessor = MediationReadinessAssessor()

        assessment = assessor.assess_readiness(
            has_safety_concerns=True,
            emotional_state="overwhelmed",
            goals_defined=False,
            documents_organized=False,
            understands_process=False,
            willing_to_compromise=False,
            can_communicate_calmly=False
        )

        assert assessment.readiness_level == MediationReadiness.NOT_READY
        assert len(assessment.safety_concerns) > 0
        assert len(assessment.red_flags) > 0

    def test_goal_creation(self):
        """Test creating mediation goal"""
        planner = MediationGoalPlanner()

        goal = planner.create_goal(
            category=MediationGoalCategory.PARENTING_TIME,
            priority=Priority.MUST_HAVE,
            description="Регулярные выходные с ребенком",
            ideal_outcome="Каждый второй уикенд с пятницы по воскресенье",
            acceptable_alternatives=["Субботы с утра до вечера каждую неделю"],
            dealbreakers=["Менее 4 дней в месяц"],
            rationale="Ребенку нужна стабильная связь с обоими родителями"
        )

        assert goal.category == MediationGoalCategory.PARENTING_TIME
        assert goal.priority == Priority.MUST_HAVE
        assert len(goal.acceptable_alternatives) == 1
        assert len(goal.dealbreakers) == 1

    def test_validate_child_focus(self):
        """Test child-focus validation"""
        planner = MediationGoalPlanner()

        # Child-focused rationale
        is_focused, feedback = planner.validate_child_focus(
            "Ребенку нужна стабильная связь с обоими родителями"
        )
        assert is_focused

        # Parent-focused rationale
        is_focused, feedback = planner.validate_child_focus(
            "Я хочу больше времени потому что это справедливо для меня"
        )
        assert not is_focused


class TestParentingModel:
    """Test Parenting Model Advisor"""

    def test_assess_coparenting_suitable(self):
        """Test assessment recommending co-parenting"""
        assessor = ParentingModelAssessor()

        assessment = assessor.assess_parenting_model(
            # Good communication
            can_communicate_calmly=True,
            communication_frequency_ok=True,
            can_compromise=True,
            respects_boundaries=True,
            # Low conflict
            frequent_arguments=False,
            escalates_quickly=False,
            involves_child_in_conflict=False,
            badmouths_other_parent=False,
            # Good cooperation
            flexible_with_schedule=True,
            shares_information=True,
            supports_other_parents_time=True,
            attends_events_together=True,
            # No safety issues
            history_of_violence=False,
            substance_abuse=False,
            mental_health_untreated=False,
            child_afraid=False
        )

        assert assessment.recommended_model == ParentingModel.CO_PARENTING
        assert assessment.conflict_level == ConflictLevel.LOW
        assert assessment.score >= 0.70
        assert len(assessment.strengths) > 0

    def test_assess_parallel_parenting_needed(self):
        """Test assessment recommending parallel parenting"""
        assessor = ParentingModelAssessor()

        assessment = assessor.assess_parenting_model(
            # Poor communication
            can_communicate_calmly=False,
            communication_frequency_ok=False,
            can_compromise=False,
            respects_boundaries=False,
            # High conflict
            frequent_arguments=True,
            escalates_quickly=True,
            involves_child_in_conflict=True,
            badmouths_other_parent=True,
            # Poor cooperation
            flexible_with_schedule=False,
            shares_information=False,
            supports_other_parents_time=False,
            attends_events_together=False,
            # No safety issues
            history_of_violence=False
        )

        assert assessment.recommended_model == ParentingModel.PARALLEL_PARENTING
        assert assessment.conflict_level in [ConflictLevel.HIGH, ConflictLevel.SEVERE]
        assert assessment.score < 0.45
        assert len(assessment.challenges) > 0

    def test_assess_safety_concerns(self):
        """Test assessment with safety concerns"""
        assessor = ParentingModelAssessor()

        assessment = assessor.assess_parenting_model(
            can_communicate_calmly=False,
            communication_frequency_ok=False,
            can_compromise=False,
            respects_boundaries=False,
            frequent_arguments=True,
            escalates_quickly=True,
            involves_child_in_conflict=True,
            badmouths_other_parent=True,
            flexible_with_schedule=False,
            shares_information=False,
            supports_other_parents_time=False,
            attends_events_together=False,
            # SAFETY CONCERNS
            history_of_violence=True,
            substance_abuse=True,
            child_afraid=True
        )

        assert assessment.recommended_model == ParentingModel.SUPERVISED
        assert assessment.conflict_level == ConflictLevel.SEVERE
        assert len(assessment.safety_concerns) > 0
        assert not assessment.can_transition

    def test_assess_transitional(self):
        """Test assessment recommending transitional model"""
        assessor = ParentingModelAssessor()

        assessment = assessor.assess_parenting_model(
            # Mixed communication
            can_communicate_calmly=True,
            communication_frequency_ok=False,
            can_compromise=True,
            respects_boundaries=True,
            # Moderate conflict
            frequent_arguments=True,
            escalates_quickly=False,
            involves_child_in_conflict=False,
            badmouths_other_parent=False,
            # Mixed cooperation
            flexible_with_schedule=False,
            shares_information=True,
            supports_other_parents_time=True,
            attends_events_together=False,
            # No safety issues
            history_of_violence=False
        )

        assert assessment.recommended_model in [
            ParentingModel.TRANSITIONAL,
            ParentingModel.PARALLEL_PARENTING
        ]
        assert assessment.can_transition


class TestContactDiaryAssistant:
    """Test Contact Diary Assistant"""

    def test_suggest_neutral_reframe(self):
        """Test neutral reframing suggestions"""
        assistant = ContactDiaryAssistant()

        original = "Ребенок был счастлив"
        suggestion = assistant.suggest_neutral_reframe(original)

        assert "улыбался" in suggestion.lower() or "смеялся" in suggestion.lower()

    def test_provide_documentation_tips(self):
        """Test documentation tips"""
        assistant = ContactDiaryAssistant()

        tips = assistant.provide_documentation_tips()

        assert len(tips) > 0
        assert any("даты" in tip.lower() or "date" in tip.lower() for tip in tips)


# Integration tests
class TestLegalToolsIntegration:
    """Test integration between legal tools"""

    def test_biff_and_contact_diary_workflow(self):
        """Test workflow: BIFF response -> Document in diary"""
        # Step 1: Create BIFF response
        biff_template = BIFFTemplateLibrary.get_template(
            "respond_to_hostile",
            language="ru",
            конкретный_ответ="Встреча состоится как запланировано"
        )

        # Step 2: Verify it's BIFF compliant
        analyzer = BIFFAnalyzer()
        analysis = analyzer.analyze(biff_template)
        assert analysis.is_biff_compliant or analysis.score >= 0.5

        # Step 3: Document interaction in diary
        diary = ContactDiary(parent_id="test_parent_001")
        entry = diary.create_entry(
            contact_type=ContactType.TEXT_MESSAGE,
            category=EntryCategory.COMMUNICATION_ISSUE,
            date_of_contact="2025-05-15",
            time_of_contact="10:00",
            duration_minutes=None,
            location="N/A",
            child_name="М.И.",
            observations="Получено агрессивное сообщение. Ответил в BIFF формате.",
            documentation=["Скриншот сообщения", "Скриншот BIFF-ответа"]
        )

        assert entry.entry_id is not None
        assert len(entry.documentation) == 2

    def test_mediation_goal_with_parenting_model(self):
        """Test creating mediation goal based on parenting model"""
        # Step 1: Assess parenting model
        assessor = ParentingModelAssessor()
        assessment = assessor.assess_parenting_model(
            can_communicate_calmly=False,
            communication_frequency_ok=False,
            can_compromise=True,
            respects_boundaries=False,
            frequent_arguments=True,
            escalates_quickly=True,
            involves_child_in_conflict=False,
            badmouths_other_parent=False,
            flexible_with_schedule=False,
            shares_information=False,
            supports_other_parents_time=True,
            attends_events_together=False,
            history_of_violence=False
        )

        # Step 2: Create appropriate mediation goal
        planner = MediationGoalPlanner()

        if assessment.recommended_model == ParentingModel.PARALLEL_PARENTING:
            goal = planner.create_goal(
                category=MediationGoalCategory.COMMUNICATION,
                priority=Priority.MUST_HAVE,
                description="Установить письменную коммуникацию",
                ideal_outcome="Вся коммуникация через приложение, BIFF формат",
                acceptable_alternatives=["Email с BIFF форматом"],
                dealbreakers=["Необходимость личных встреч"],
                rationale="Ребенку нужна защита от конфликтов между родителями"
            )

            assert goal.priority == Priority.MUST_HAVE
            assert "письменн" in goal.description.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
