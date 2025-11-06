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
        usage = UsageMetrics(
            total_messages=self.usage_counters['total_messages'],
            active_users=len(self.active_users),
            techniques_distribution=dict(self.techniques_used),
            emotions_detected=dict(self.emotions_detected),
            peak_hour=max(self.hourly_messages.items(), key=lambda x: x[1])[0] if self.hourly_messages else 0
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
        self.response_times.clear()
        self.empathy_scores.clear()
        self.safety_scores.clear()
        self.therapeutic_scores.clear()
        self.risk_scores.clear()
        self.techniques_used.clear()
        self.emotions_detected.clear()
        self.hourly_messages.clear()
        self.active_users.clear()

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
