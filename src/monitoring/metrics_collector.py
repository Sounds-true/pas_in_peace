"""
Metrics collection for bot monitoring.

Sprint 5 Week 3: Metrics & Observability
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics


@dataclass
class SafetyMetrics:
    """Safety-related metrics."""
    crisis_detections: int = 0
    suicide_assessments: int = 0
    violence_assessments: int = 0
    guardrails_activations: int = 0
    pii_warnings: int = 0
    false_positives: int = 0
    crisis_detection_rate: float = 0.0
    avg_risk_score: float = 0.0


@dataclass
class QualityMetrics:
    """Quality-related metrics."""
    supervisor_approvals: int = 0
    supervisor_rejections: int = 0
    avg_empathy_score: float = 0.0
    avg_safety_score: float = 0.0
    avg_therapeutic_value: float = 0.0
    avg_accuracy_score: float = 0.0
    avg_autonomy_score: float = 0.0
    avg_boundary_score: float = 0.0


@dataclass
class UsageMetrics:
    """Usage-related metrics."""
    total_messages: int = 0
    total_sessions: int = 0
    active_users: int = 0
    avg_messages_per_session: float = 0.0
    avg_session_duration: float = 0.0
    techniques_distribution: Dict[str, int] = field(default_factory=dict)
    emotions_detected: Dict[str, int] = field(default_factory=dict)
    peak_hour: int = 0
    # NEW: Conversion metrics
    letters_started: int = 0
    letters_completed: int = 0
    goals_created: int = 0
    conversion_rate_letters: float = 0.0
    conversion_rate_goals: float = 0.0


@dataclass
class TechnicalMetrics:
    """Technical performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    error_rate: float = 0.0
    api_calls_openai: int = 0
    avg_tokens_per_request: float = 0.0


@dataclass
class BotMetrics:
    """Complete bot metrics."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    period: str = "1h"  # Time period for these metrics
    safety: SafetyMetrics = field(default_factory=SafetyMetrics)
    quality: QualityMetrics = field(default_factory=QualityMetrics)
    usage: UsageMetrics = field(default_factory=UsageMetrics)
    technical: TechnicalMetrics = field(default_factory=TechnicalMetrics)


class MetricsCollector:
    """
    Collects and aggregates bot metrics.

    Usage:
        collector = MetricsCollector()
        await collector.record_crisis_detection(user_id, risk_level)
        await collector.record_supervisor_decision(approved, scores)
        metrics = await collector.get_metrics(period="1h")
    """

    def __init__(self, window_size: int = 1000):
        """
        Initialize metrics collector.

        Args:
            window_size: Number of recent data points to keep for calculations
        """
        self.window_size = window_size

        # Counters
        self.safety_counters = defaultdict(int)
        self.quality_counters = defaultdict(int)
        self.usage_counters = defaultdict(int)
        self.technical_counters = defaultdict(int)

        # Recent values for percentile calculations
        self.response_times: deque = deque(maxlen=window_size)
        self.empathy_scores: deque = deque(maxlen=window_size)
        self.safety_scores: deque = deque(maxlen=window_size)
        self.therapeutic_scores: deque = deque(maxlen=window_size)
        self.risk_scores: deque = deque(maxlen=window_size)

        # Distributions
        self.techniques_used = defaultdict(int)
        self.emotions_detected = defaultdict(int)
        self.hourly_messages = defaultdict(int)

        # Active users tracking
        self.active_users = set()

        # Conversion tracking
        self.conversion_counters = defaultdict(int)

        # Session tracking
        self.session_durations: deque = deque(maxlen=window_size)

        # Emotional tracking
        self.emotional_scores: deque = deque(maxlen=window_size)
        self.distress_levels: deque = deque(maxlen=window_size)

    async def record_crisis_detection(
        self,
        user_id: str,
        risk_level: str,
        risk_score: float = 0.0
    ):
        """Record a crisis detection event."""
        self.safety_counters['crisis_detections'] += 1

        if 'suicide' in risk_level.lower():
            self.safety_counters['suicide_assessments'] += 1
        elif 'violence' in risk_level.lower():
            self.safety_counters['violence_assessments'] += 1

        self.risk_scores.append(risk_score)

    async def record_guardrails_activation(self, rule_triggered: str):
        """Record guardrails activation."""
        self.safety_counters['guardrails_activations'] += 1

    async def record_pii_warning(self, user_id: str, entity_types: List[str]):
        """Record PII warning given to user."""
        self.safety_counters['pii_warnings'] += 1

    async def record_supervisor_decision(
        self,
        approved: bool,
        scores: Dict[str, float]
    ):
        """Record supervisor agent decision."""
        if approved:
            self.quality_counters['approvals'] += 1
        else:
            self.quality_counters['rejections'] += 1

        # Record scores
        if 'empathy' in scores:
            self.empathy_scores.append(scores['empathy'])
        if 'safety' in scores:
            self.safety_scores.append(scores['safety'])
        if 'therapeutic_value' in scores:
            self.therapeutic_scores.append(scores['therapeutic_value'])

    async def record_message(
        self,
        user_id: str,
        technique_used: Optional[str] = None,
        emotion_detected: Optional[str] = None
    ):
        """Record a message interaction."""
        self.usage_counters['total_messages'] += 1
        self.active_users.add(user_id)

        if technique_used:
            self.techniques_used[technique_used] += 1

        if emotion_detected:
            self.emotions_detected[emotion_detected] += 1

        # Track hourly distribution
        current_hour = datetime.utcnow().hour
        self.hourly_messages[current_hour] += 1

    async def record_response_time(self, response_time: float):
        """Record response time in seconds."""
        self.response_times.append(response_time)
        self.technical_counters['total_requests'] += 1
        self.technical_counters['successful_requests'] += 1

    async def record_error(self, error_type: str):
        """Record an error."""
        self.technical_counters['failed_requests'] += 1
        self.technical_counters['total_requests'] += 1

    async def record_openai_call(self, tokens_used: int):
        """Record OpenAI API call."""
        self.technical_counters['openai_calls'] += 1
        self.technical_counters['total_tokens'] = \
            self.technical_counters.get('total_tokens', 0) + tokens_used

    async def record_letter_started(self, user_id: str):
        """Record that a user started writing a letter."""
        self.conversion_counters['letters_started'] += 1

    async def record_letter_completed(self, user_id: str):
        """Record that a user completed a letter."""
        self.conversion_counters['letters_completed'] += 1

    async def record_goal_created(self, user_id: str):
        """Record that a user created a goal."""
        self.conversion_counters['goals_created'] += 1

    async def record_session_duration(self, duration_minutes: float):
        """Record session duration in minutes."""
        self.session_durations.append(duration_minutes)
        self.usage_counters['total_sessions'] += 1

    async def record_emotional_state(
        self,
        emotional_score: float,
        distress_level: float
    ):
        """
        Record emotional state metrics.

        Args:
            emotional_score: 0-1 scale (higher is better)
            distress_level: 0-1 scale (higher is worse)
        """
        self.emotional_scores.append(emotional_score)
        self.distress_levels.append(distress_level)

    async def get_metrics(self, period: str = "1h") -> BotMetrics:
        """
        Get current metrics.

        Args:
            period: Time period for metrics (e.g., "1h", "24h")

        Returns:
            BotMetrics object with all current metrics
        """
        # Safety metrics
        safety = SafetyMetrics(
            crisis_detections=self.safety_counters['crisis_detections'],
            suicide_assessments=self.safety_counters['suicide_assessments'],
            violence_assessments=self.safety_counters['violence_assessments'],
            guardrails_activations=self.safety_counters['guardrails_activations'],
            pii_warnings=self.safety_counters['pii_warnings'],
            avg_risk_score=statistics.mean(self.risk_scores) if self.risk_scores else 0.0
        )

        # Quality metrics
        total_decisions = self.quality_counters['approvals'] + self.quality_counters['rejections']
        quality = QualityMetrics(
            supervisor_approvals=self.quality_counters['approvals'],
            supervisor_rejections=self.quality_counters['rejections'],
            avg_empathy_score=statistics.mean(self.empathy_scores) if self.empathy_scores else 0.0,
            avg_safety_score=statistics.mean(self.safety_scores) if self.safety_scores else 0.0,
            avg_therapeutic_value=statistics.mean(self.therapeutic_scores) if self.therapeutic_scores else 0.0
        )

        # Usage metrics
        total_messages = self.usage_counters['total_messages']
        total_sessions = self.usage_counters['total_sessions']
        letters_started = self.conversion_counters['letters_started']
        letters_completed = self.conversion_counters['letters_completed']
        goals_created = self.conversion_counters['goals_created']

        # Calculate conversion rates
        conversion_rate_letters = (letters_completed / total_messages * 100) if total_messages > 0 else 0.0
        conversion_rate_goals = (goals_created / total_messages * 100) if total_messages > 0 else 0.0

        usage = UsageMetrics(
            total_messages=total_messages,
            total_sessions=total_sessions,
            active_users=len(self.active_users),
            avg_messages_per_session=(total_messages / total_sessions) if total_sessions > 0 else 0.0,
            avg_session_duration=statistics.mean(self.session_durations) if self.session_durations else 0.0,
            techniques_distribution=dict(self.techniques_used),
            emotions_detected=dict(self.emotions_detected),
            peak_hour=max(self.hourly_messages.items(), key=lambda x: x[1])[0] if self.hourly_messages else 0,
            letters_started=letters_started,
            letters_completed=letters_completed,
            goals_created=goals_created,
            conversion_rate_letters=conversion_rate_letters,
            conversion_rate_goals=conversion_rate_goals
        )

        # Technical metrics
        response_times_list = list(self.response_times)
        total_requests = self.technical_counters['total_requests']
        failed_requests = self.technical_counters['failed_requests']

        technical = TechnicalMetrics(
            total_requests=total_requests,
            successful_requests=self.technical_counters['successful_requests'],
            failed_requests=failed_requests,
            error_rate=(failed_requests / total_requests * 100) if total_requests > 0 else 0.0,
            avg_response_time=statistics.mean(response_times_list) if response_times_list else 0.0,
            p50_response_time=statistics.median(response_times_list) if response_times_list else 0.0,
            p95_response_time=self._percentile(response_times_list, 0.95) if response_times_list else 0.0,
            p99_response_time=self._percentile(response_times_list, 0.99) if response_times_list else 0.0,
            api_calls_openai=self.technical_counters['openai_calls'],
            avg_tokens_per_request=(
                self.technical_counters.get('total_tokens', 0) /
                self.technical_counters['openai_calls']
            ) if self.technical_counters['openai_calls'] > 0 else 0.0
        )

        return BotMetrics(
            period=period,
            safety=safety,
            quality=quality,
            usage=usage,
            technical=technical
        )

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    async def reset_metrics(self):
        """Reset all metrics (for new period)."""
        self.safety_counters.clear()
        self.quality_counters.clear()
        self.usage_counters.clear()
        self.technical_counters.clear()
        self.conversion_counters.clear()
        self.response_times.clear()
        self.empathy_scores.clear()
        self.safety_scores.clear()
        self.therapeutic_scores.clear()
        self.risk_scores.clear()
        self.techniques_used.clear()
        self.emotions_detected.clear()
        self.hourly_messages.clear()
        self.active_users.clear()
        self.session_durations.clear()
        self.emotional_scores.clear()
        self.distress_levels.clear()

    async def export_metrics(self, format: str = "dict") -> Dict:
        """
        Export metrics in specified format.

        Args:
            format: "dict", "json", or "prometheus"

        Returns:
            Metrics in requested format
        """
        metrics = await self.get_metrics()

        if format == "dict":
            return asdict(metrics)
        elif format == "json":
            import json
            return json.dumps(asdict(metrics), default=str, indent=2)
        elif format == "prometheus":
            return self._to_prometheus(metrics)
        else:
            return asdict(metrics)

    def _to_prometheus(self, metrics: BotMetrics) -> str:
        """Convert metrics to Prometheus format."""
        lines = []

        # Safety metrics
        lines.append(f"bot_crisis_detections_total {metrics.safety.crisis_detections}")
        lines.append(f"bot_suicide_assessments_total {metrics.safety.suicide_assessments}")
        lines.append(f"bot_pii_warnings_total {metrics.safety.pii_warnings}")

        # Quality metrics
        lines.append(f"bot_avg_empathy_score {metrics.quality.avg_empathy_score}")
        lines.append(f"bot_avg_safety_score {metrics.quality.avg_safety_score}")

        # Technical metrics
        lines.append(f"bot_response_time_seconds_p95 {metrics.technical.p95_response_time}")
        lines.append(f"bot_error_rate_percent {metrics.technical.error_rate}")

        return "\n".join(lines)

    async def save_snapshot_to_db(self, db_manager, period: str = "1h"):
        """
        Save current metrics snapshot to database.

        Args:
            db_manager: DatabaseManager instance
            period: Time period for this snapshot
        """
        from src.storage.models import MetricsSnapshot
        from datetime import datetime

        metrics = await self.get_metrics(period=period)

        # Calculate most used technique and emotion
        most_used_technique = max(
            self.techniques_used.items(),
            key=lambda x: x[1]
        )[0] if self.techniques_used else None

        most_detected_emotion = max(
            self.emotions_detected.items(),
            key=lambda x: x[1]
        )[0] if self.emotions_detected else None

        # Calculate average emotional metrics
        avg_emotional_score = statistics.mean(self.emotional_scores) if self.emotional_scores else 0.0
        avg_distress_level = statistics.mean(self.distress_levels) if self.distress_levels else 0.0

        snapshot = MetricsSnapshot(
            timestamp=datetime.utcnow(),
            period=period,
            # Usage metrics
            total_messages=metrics.usage.total_messages,
            total_sessions=metrics.usage.total_sessions,
            active_users=metrics.usage.active_users,
            avg_messages_per_session=metrics.usage.avg_messages_per_session,
            avg_session_duration_minutes=metrics.usage.avg_session_duration,
            techniques_distribution=metrics.usage.techniques_distribution,
            # Conversion metrics
            conversations_total=metrics.usage.total_sessions,
            letters_started=metrics.usage.letters_started,
            letters_completed=metrics.usage.letters_completed,
            goals_created=metrics.usage.goals_created,
            conversion_rate_letters=metrics.usage.conversion_rate_letters,
            conversion_rate_goals=metrics.usage.conversion_rate_goals,
            # Emotional trends
            emotions_detected=metrics.usage.emotions_detected,
            avg_emotional_score=avg_emotional_score,
            avg_distress_level=avg_distress_level,
            # Safety metrics
            crisis_detections=metrics.safety.crisis_detections,
            pii_warnings=metrics.safety.pii_warnings,
            # Quality metrics
            avg_empathy_score=metrics.quality.avg_empathy_score,
            avg_safety_score=metrics.quality.avg_safety_score,
            avg_therapeutic_value=metrics.quality.avg_therapeutic_value,
            # Technical metrics
            total_requests=metrics.technical.total_requests,
            failed_requests=metrics.technical.failed_requests,
            avg_response_time_seconds=metrics.technical.avg_response_time,
            p95_response_time_seconds=metrics.technical.p95_response_time,
            error_rate_percent=metrics.technical.error_rate,
            api_calls_openai=metrics.technical.api_calls_openai,
            # Additional analytics
            peak_hour=metrics.usage.peak_hour,
            most_used_technique=most_used_technique,
            most_detected_emotion=most_detected_emotion
        )

        # Save to database
        async with db_manager.session() as db_session:
            db_session.add(snapshot)
            await db_session.commit()

        return snapshot

    async def get_analytics(
        self,
        db_manager,
        period_days: int = 7,
        metric_type: str = "all"
    ) -> Dict:
        """
        Get analytics from database for specified period.

        Args:
            db_manager: DatabaseManager instance
            period_days: Number of days to include in analytics
            metric_type: Type of metrics to retrieve ("conversions", "emotions", "techniques", "all")

        Returns:
            Dictionary with analytics data
        """
        from src.storage.models import MetricsSnapshot
        from sqlalchemy import select
        from datetime import datetime, timedelta

        start_date = datetime.utcnow() - timedelta(days=period_days)

        async with db_manager.session() as db_session:
            stmt = select(MetricsSnapshot).where(
                MetricsSnapshot.timestamp >= start_date
            ).order_by(MetricsSnapshot.timestamp.asc())

            result = await db_session.execute(stmt)
            snapshots = list(result.scalars().all())

        if not snapshots:
            return {"error": "No data available for this period"}

        analytics = {
            "period_start": start_date.isoformat(),
            "period_end": datetime.utcnow().isoformat(),
            "total_snapshots": len(snapshots)
        }

        if metric_type in ["conversions", "all"]:
            analytics["conversions"] = {
                "total_letters_completed": sum(s.letters_completed for s in snapshots),
                "total_goals_created": sum(s.goals_created for s in snapshots),
                "avg_conversion_rate_letters": statistics.mean(
                    s.conversion_rate_letters for s in snapshots if s.conversion_rate_letters > 0
                ) if any(s.conversion_rate_letters > 0 for s in snapshots) else 0.0,
                "avg_conversion_rate_goals": statistics.mean(
                    s.conversion_rate_goals for s in snapshots if s.conversion_rate_goals > 0
                ) if any(s.conversion_rate_goals > 0 for s in snapshots) else 0.0,
                "trend": self._calculate_trend([s.conversion_rate_letters for s in snapshots])
            }

        if metric_type in ["emotions", "all"]:
            analytics["emotions"] = {
                "avg_emotional_score": statistics.mean(s.avg_emotional_score for s in snapshots),
                "avg_distress_level": statistics.mean(s.avg_distress_level for s in snapshots),
                "emotional_trend": self._calculate_trend([s.avg_emotional_score for s in snapshots]),
                "distress_trend": self._calculate_trend([s.avg_distress_level for s in snapshots]),
                "most_common_emotions": self._aggregate_distributions(
                    [s.emotions_detected for s in snapshots]
                )
            }

        if metric_type in ["techniques", "all"]:
            analytics["techniques"] = {
                "usage_distribution": self._aggregate_distributions(
                    [s.techniques_distribution for s in snapshots]
                ),
                "most_used": snapshots[-1].most_used_technique if snapshots else None,
                "total_messages": sum(s.total_messages for s in snapshots),
                "avg_messages_per_session": statistics.mean(
                    s.avg_messages_per_session for s in snapshots if s.avg_messages_per_session > 0
                ) if any(s.avg_messages_per_session > 0 for s in snapshots) else 0.0
            }

        if metric_type == "all":
            analytics["quality"] = {
                "avg_empathy": statistics.mean(s.avg_empathy_score for s in snapshots),
                "avg_safety": statistics.mean(s.avg_safety_score for s in snapshots),
                "avg_therapeutic_value": statistics.mean(s.avg_therapeutic_value for s in snapshots)
            }

            analytics["safety"] = {
                "total_crisis_detections": sum(s.crisis_detections for s in snapshots),
                "total_pii_warnings": sum(s.pii_warnings for s in snapshots)
            }

        return analytics

    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calculate trend direction from list of values.

        Returns:
            "increasing", "decreasing", or "stable"
        """
        if len(values) < 2:
            return "insufficient_data"

        # Simple linear trend
        first_half = statistics.mean(values[:len(values)//2])
        second_half = statistics.mean(values[len(values)//2:])

        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _aggregate_distributions(self, distributions: List[Dict]) -> Dict:
        """Aggregate multiple distribution dictionaries."""
        aggregated = defaultdict(int)
        for dist in distributions:
            if dist:
                for key, value in dist.items():
                    aggregated[key] += value
        return dict(aggregated)
