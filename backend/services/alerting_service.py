"""
Alerting Service for system anomalies.

This service sends alerts when system thresholds are exceeded:
- Latency > threshold
- Error rate > threshold  
- Cost > threshold
- Queue length > threshold

Supports multiple notification channels:
- Slack webhooks
- Email (via SMTP)
- PagerDuty
"""

import os
import smtplib
import threading
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# Alert Types
# =========================================================

class AlertLevel:
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Alert:
    """Represents a single alert."""
    
    def __init__(
        self,
        level: str,
        message: str,
        metric_name: Optional[str] = None,
        metric_value: Optional[float] = None,
        threshold: Optional[float] = None,
    ):
        self.level = level
        self.message = message
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.threshold = threshold
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "message": self.message,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp.isoformat(),
        }


# =========================================================
# Slack Notifier
# =========================================================

class SlackNotifier:
    """Sends alerts to Slack via webhooks."""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)
    
    def send(self, alert: Alert):
        """Send alert to Slack."""
        if not self.enabled:
            return
        
        # Determine color based on level
        color = {
            AlertLevel.INFO: "#36a64f",
            AlertLevel.WARNING: "#ff9800",
            AlertLevel.ERROR: "#f44336",
            AlertLevel.CRITICAL: "#d32f2f",
        }.get(alert.level, "#cccccc")
        
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"Intervux AI Alert: {alert.level.upper()}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Metric", "value": alert.metric_name or "N/A", "short": True},
                        {"title": "Value", "value": str(alert.metric_value) if alert.metric_value is not None else "N/A", "short": True},
                        {"title": "Threshold", "value": str(alert.threshold) if alert.threshold is not None else "N/A", "short": True},
                    ],
                    "footer": "Intervux AI",
                    "ts": int(alert.timestamp.timestamp()),
                }
            ]
        }
        
        try:
            import json
            data = json.dumps(payload).encode("utf-8")
            req = Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"})
            urlopen(req, timeout=5)
        except URLError:
            logger.exception("Slack alert send failed")


# =========================================================
# Email Notifier
# =========================================================

class EmailNotifier:
    """Sends alerts via email."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("ALERT_FROM_EMAIL", self.smtp_user)
        self.to_emails = os.getenv("ALERT_TO_EMAILS", "").split(",")
        self.enabled = bool(self.smtp_user and self.smtp_password and self.to_emails)
    
    def send(self, alert: Alert):
        """Send alert via email."""
        if not self.enabled:
            return
        
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = ", ".join(self.to_emails)
        msg["Subject"] = f"[Intervux AI] {alert.level.upper()}: {alert.message[:50]}"
        
        body = f"""
Intervux AI Alert

Level: {alert.level.upper()}
Message: {alert.message}
Metric: {alert.metric_name}
Value: {alert.metric_value}
Threshold: {alert.threshold}
Timestamp: {alert.timestamp.isoformat()}
"""
        msg.attach(MIMEText(body, "plain"))
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception:
            logger.exception("Email alert send failed")


# =========================================================
# PagerDuty Notifier
# =========================================================

class PagerDutyNotifier:
    """Sends alerts to PagerDuty."""
    
    def __init__(self):
        self.api_key = os.getenv("PAGERDUTY_API_KEY")
        self.service_id = os.getenv("PAGERDUTY_SERVICE_ID")
        self.enabled = bool(self.api_key and self.service_id)
    
    def send(self, alert: Alert):
        """Send alert to PagerDuty."""
        if not self.enabled:
            return
        
        severity = {
            AlertLevel.INFO: "info",
            AlertLevel.WARNING: "warning",
            AlertLevel.ERROR: "error",
            AlertLevel.CRITICAL: "critical",
        }.get(alert.level, "info")
        
        payload = {
            "routing_key": self.service_id,
            "event_action": "trigger",
            "payload": {
                "summary": alert.message,
                "severity": severity,
                "source": "intervux-ai",
                "custom_details": alert.to_dict(),
            },
        }
        
        try:
            import json
            import urllib.request
            data = json.dumps(payload).encode("utf-8")
            req = Request(
                "https://events.pagerduty.com/v2/enqueue",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Token token={self.api_key}",
                }
            )
            urlopen(req, timeout=5)
        except URLError:
            logger.exception("PagerDuty alert send failed")


# =========================================================
# Alerting Service
# =========================================================

class AlertingService:
    """
    Main alerting service that checks thresholds and sends notifications.
    
    Example usage:
        alerting = AlertingService()
        
        # Check metrics and send alerts if needed
        alerting.check_and_alert(
            latency_p95=4.5,
            error_rate=3.2,
            daily_cost=550.0,
            queue_length=8,
        )
    """
    
    def __init__(self):
        self.slack = SlackNotifier()
        self.email = EmailNotifier()
        self.pagerduty = PagerDutyNotifier()
        
        # Thresholds from environment
        self.latency_threshold = float(os.getenv("ALERT_LATENCY_P95_S", "3.0"))
        self.error_threshold = float(os.getenv("ALERT_ERROR_RATE_PCT", "2.0"))
        self.cost_threshold = float(os.getenv("ALERT_DAILY_COST", "500.0"))
        self.queue_threshold = float(os.getenv("ALERT_QUEUE_LENGTH", "5"))
        
        # Cooldown to avoid spam (in seconds)
        self.cooldown_seconds = int(os.getenv("ALERT_COOLDOWN_SECONDS", "300"))
        self._last_alerts: Dict[str, float] = {}
        self._lock = threading.Lock()
    
    def _should_send_alert(self, metric_name: str) -> bool:
        """Check if we should send an alert (respects cooldown)."""
        with self._lock:
            now = datetime.utcnow().timestamp()
            last_alert = self._last_alerts.get(metric_name, 0)
            if now - last_alert < self.cooldown_seconds:
                return False
            self._last_alerts[metric_name] = now
            return True
    
    def check_and_alert(
        self,
        latency_p95: Optional[float] = None,
        error_rate: Optional[float] = None,
        daily_cost: Optional[float] = None,
        queue_length: Optional[float] = None,
        active_sessions: Optional[float] = None,
    ):
        """
        Check metrics against thresholds and send alerts if exceeded.
        
        Args:
            latency_p95: P95 latency in seconds
            error_rate: Error rate percentage
            daily_cost: Daily cost in USD
            queue_length: Current queue length
            active_sessions: Number of active sessions
        """
        alerts = []
        
        # Check latency
        if latency_p95 is not None and latency_p95 > self.latency_threshold:
            if self._should_send_alert("latency"):
                level = AlertLevel.CRITICAL if latency_p95 > self.latency_threshold * 2 else AlertLevel.ERROR
                alerts.append(Alert(
                    level=level,
                    message=f"P95 latency ({latency_p95:.2f}s) exceeds threshold ({self.latency_threshold}s)",
                    metric_name="latency_p95",
                    metric_value=latency_p95,
                    threshold=self.latency_threshold,
                ))
        
        # Check error rate
        if error_rate is not None and error_rate > self.error_threshold:
            if self._should_send_alert("error_rate"):
                level = AlertLevel.CRITICAL if error_rate > self.error_threshold * 2 else AlertLevel.ERROR
                alerts.append(Alert(
                    level=level,
                    message=f"Error rate ({error_rate:.2f}%) exceeds threshold ({self.error_threshold}%)",
                    metric_name="error_rate",
                    metric_value=error_rate,
                    threshold=self.error_threshold,
                ))
        
        # Check daily cost
        if daily_cost is not None and daily_cost > self.cost_threshold:
            if self._should_send_alert("daily_cost"):
                level = AlertLevel.WARNING
                if daily_cost > self.cost_threshold * 2:
                    level = AlertLevel.CRITICAL
                alerts.append(Alert(
                    level=level,
                    message=f"Daily AI spend (${daily_cost:.2f}) exceeds threshold (${self.cost_threshold})",
                    metric_name="daily_cost",
                    metric_value=daily_cost,
                    threshold=self.cost_threshold,
                ))
        
        # Check queue length
        if queue_length is not None and queue_length > self.queue_threshold:
            if self._should_send_alert("queue_length"):
                level = AlertLevel.WARNING
                if queue_length > self.queue_threshold * 2:
                    level = AlertLevel.ERROR
                alerts.append(Alert(
                    level=level,
                    message=f"Queue length ({queue_length:.0f}) exceeds threshold ({self.queue_threshold:.0f})",
                    metric_name="queue_length",
                    metric_value=queue_length,
                    threshold=self.queue_threshold,
                ))
        
        # Check active sessions
        max_sessions = float(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
        if active_sessions is not None and active_sessions >= max_sessions:
            if self._should_send_alert("active_sessions"):
                alerts.append(Alert(
                    level=AlertLevel.WARNING,
                    message=f"Active sessions ({active_sessions:.0f}) at capacity ({max_sessions})",
                    metric_name="active_sessions",
                    metric_value=active_sessions,
                    threshold=max_sessions,
                ))
        
        # Send all alerts
        for alert in alerts:
            self._send_alert(alert)
    
    def _send_alert(self, alert: Alert):
        """Send alert to all configured notifiers."""
        # Send to Slack
        thread = threading.Thread(target=self.slack.send, args=(alert,))
        thread.start()
        
        # Send to Email
        thread = threading.Thread(target=self.email.send, args=(alert,))
        thread.start()
        
        # Send to PagerDuty
        thread = threading.Thread(target=self.pagerduty.send, args=(alert,))
        thread.start()
    
    def send_test_alert(self, channel: str = "slack"):
        """
        Send a test alert.
        
        Args:
            channel: Channel to test (slack, email, pagerduty)
        """
        test_alert = Alert(
            level=AlertLevel.INFO,
            message="This is a test alert from Intervux AI",
            metric_name="test",
            metric_value=1.0,
            threshold=0.0,
        )
        
        if channel == "slack":
            self.slack.send(test_alert)
        elif channel == "email":
            self.email.send(test_alert)
        elif channel == "pagerduty":
            self.pagerduty.send(test_alert)


# Singleton instance
alerting_service = AlertingService()


# =========================================================
# Convenience Functions
# =========================================================

def check_metrics_and_alert(
    latency_p95: Optional[float] = None,
    error_rate: Optional[float] = None,
    daily_cost: Optional[float] = None,
    queue_length: Optional[float] = None,
    active_sessions: Optional[float] = None,
):
    """
    Convenience function to check metrics and send alerts.
    
    Args:
        latency_p95: P95 latency in seconds
        error_rate: Error rate percentage
        daily_cost: Daily cost in USD
        queue_length: Current queue length
        active_sessions: Number of active sessions
    """
    alerting_service.check_and_alert(
        latency_p95=latency_p95,
        error_rate=error_rate,
        daily_cost=daily_cost,
        queue_length=queue_length,
        active_sessions=active_sessions,
    )

