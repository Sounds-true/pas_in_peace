"""
Legal Tools Module

Provides legal and practical tools for parents navigating family law:
- Contact Diary: Court-admissible documentation
- BIFF Templates: High-conflict communication management
- Mediation Prep: Preparation for family mediation
- Parenting Model Advisor: Co-parenting vs Parallel parenting guidance

Author: pas_in_peace
License: MIT
"""

from .contact_diary import (
    ContactDiary,
    ContactEntry,
    ContactType,
    EntryCategory,
    ContactDiaryAssistant,
    EXAMPLE_ENTRIES
)

from .biff_templates import (
    BIFFAnalyzer,
    BIFFTransformer,
    BIFFTemplateLibrary,
    BIFFCommunicationGuide,
    BIFFAnalysis,
    BIFFViolation,
    BIFFNVCBridge
)

from .mediation_prep import (
    MediationReadinessAssessor,
    MediationGoalPlanner,
    MediationDocumentOrganizer,
    MediationStrategyPlanner,
    MediationChecklist,
    MediationReadiness,
    MediationGoal,
    MediationGoalCategory,
    Priority,
    ReadinessAssessment,
    EXAMPLE_MEDIATION_GOALS
)

from .parenting_model_advisor import (
    ParentingModelAssessor,
    ParentingModelGuide,
    ParentingModelToolkit,
    ParentingModel,
    ConflictLevel,
    ParentingModelAssessment,
    PARENTING_MODEL_QUESTIONNAIRE
)

from .legal_tools_handler import (
    LegalToolsHandler,
    LegalToolResponse
)

__all__ = [
    # Contact Diary
    "ContactDiary",
    "ContactEntry",
    "ContactType",
    "EntryCategory",
    "ContactDiaryAssistant",
    "EXAMPLE_ENTRIES",

    # BIFF
    "BIFFAnalyzer",
    "BIFFTransformer",
    "BIFFTemplateLibrary",
    "BIFFCommunicationGuide",
    "BIFFAnalysis",
    "BIFFViolation",
    "BIFFNVCBridge",

    # Mediation
    "MediationReadinessAssessor",
    "MediationGoalPlanner",
    "MediationDocumentOrganizer",
    "MediationStrategyPlanner",
    "MediationChecklist",
    "MediationReadiness",
    "MediationGoal",
    "MediationGoalCategory",
    "Priority",
    "ReadinessAssessment",
    "EXAMPLE_MEDIATION_GOALS",

    # Parenting Model
    "ParentingModelAssessor",
    "ParentingModelGuide",
    "ParentingModelToolkit",
    "ParentingModel",
    "ConflictLevel",
    "ParentingModelAssessment",
    "PARENTING_MODEL_QUESTIONNAIRE",

    # Handler
    "LegalToolsHandler",
    "LegalToolResponse",
]
