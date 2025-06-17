#!/usr/bin/env python3
"""
QTM3 Telemetry Logger
Tracks KPIs for Phase 0 and beyond
Privacy-conscious: only aggregated metrics, no PII
"""

import sqlite3
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

class TelemetryLogger:
    """Privacy-conscious metrics collection for QTM3"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path.home() / "qtm3" / "telemetry.db"
        self.session_id = hashlib.sha256(
            f"{datetime.now().isoformat()}-{os.getpid()}".encode()
        ).hexdigest()[:12]
        self._init_db()
    
    def _init_db(self):
        """Initialize telemetry database"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT,
                    event_type TEXT,
                    duration_ms REAL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
                CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);
            """)
    
    def log_event(self, event_type: str, duration_ms: float = None, metadata: Dict = None):
        """Log a privacy-safe event"""
        # Strip any PII from metadata
        safe_metadata = self._sanitize_metadata(metadata or {})
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events (session_id, event_type, duration_ms, metadata) VALUES (?, ?, ?, ?)",
                (self.session_id, event_type, duration_ms, json.dumps(safe_metadata))
            )
    
    def log_metric(self, metric_name: str, value: float, unit: str = "count"):
        """Log a numeric metric"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO metrics (metric_name, value, unit) VALUES (?, ?, ?)",
                (metric_name, value, unit)
            )
    
    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """Remove PII, keep only aggregatable data"""
        safe_keys = {'task_count', 'energy_level', 'phase', 'feature', 'error_type'}
        return {k: v for k, v in metadata.items() if k in safe_keys}
    
    def get_capture_latency_p95(self, days: int = 7) -> float:
        """Get 95th percentile capture latency"""
        with sqlite3.connect(self.db_path) as conn:
            conn.create_function("percentile", 2, self._percentile)
            result = conn.execute("""
                SELECT percentile(duration_ms, 0.95)
                FROM events
                WHERE event_type = 'capture_task'
                AND timestamp > datetime('now', ? || ' days')
            """, (-days,)).fetchone()
        return result[0] if result[0] else 0.0
    
    def get_throughput_delta(self) -> Dict[str, float]:
        """Calculate week-over-week throughput change"""
        with sqlite3.connect(self.db_path) as conn:
            # This week
            this_week = conn.execute("""
                SELECT COUNT(*) 
                FROM events 
                WHERE event_type = 'complete_task'
                AND timestamp > datetime('now', '-7 days')
            """).fetchone()[0]
            
            # Last week
            last_week = conn.execute("""
                SELECT COUNT(*) 
                FROM events 
                WHERE event_type = 'complete_task'
                AND timestamp BETWEEN datetime('now', '-14 days') AND datetime('now', '-7 days')
            """).fetchone()[0]
            
            delta = ((this_week - last_week) / max(last_week, 1)) * 100
            
        return {
            'this_week': this_week,
            'last_week': last_week,
            'delta_percent': delta
        }
    
    def get_context_accuracy(self) -> float:
        """Calculate context tagging accuracy from user feedback"""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM events WHERE event_type = 'context_tagged'"
            ).fetchone()[0]
            
            correct = conn.execute("""
                SELECT COUNT(*) FROM events 
                WHERE event_type = 'context_feedback' 
                AND json_extract(metadata, '$.correct') = 1
            """).fetchone()[0]
            
        return (correct / max(total, 1)) * 100
    
    def get_reflection_adherence(self) -> float:
        """Calculate % of days with completed reflections"""
        with sqlite3.connect(self.db_path) as conn:
            # Days with completed tasks
            task_days = conn.execute("""
                SELECT COUNT(DISTINCT date(timestamp))
                FROM events
                WHERE event_type = 'complete_task'
                AND timestamp > datetime('now', '-30 days')
            """).fetchone()[0]
            
            # Days with reflections
            reflection_days = conn.execute("""
                SELECT COUNT(DISTINCT date(timestamp))
                FROM events
                WHERE event_type = 'daily_reflection'
                AND timestamp > datetime('now', '-30 days')
            """).fetchone()[0]
            
        return (reflection_days / max(task_days, 1)) * 100
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile of a list"""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def generate_weekly_report(self) -> str:
        """Generate privacy-safe weekly metrics report"""
        capture_p95 = self.get_capture_latency_p95()
        throughput = self.get_throughput_delta()
        context_acc = self.get_context_accuracy()
        reflection_adh = self.get_reflection_adherence()
        
        report = f"""
QTM3 Weekly Metrics Report
==========================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Performance Metrics:
- Capture Latency (P95): {capture_p95:.1f}ms
- Task Throughput: {throughput['this_week']} tasks ({throughput['delta_percent']:+.1f}% WoW)
- Context Accuracy: {context_acc:.1f}%
- Reflection Adherence: {reflection_adh:.1f}%

Session Activity:
"""
        
        # Add session summary
        with sqlite3.connect(self.db_path) as conn:
            sessions = conn.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as unique_sessions,
                    COUNT(*) as total_events,
                    AVG(duration_ms) as avg_duration
                FROM events
                WHERE timestamp > datetime('now', '-7 days')
            """).fetchone()
            
            report += f"- Active Sessions: {sessions[0]}\n"
            report += f"- Total Events: {sessions[1]}\n"
            report += f"- Avg Event Duration: {sessions[2]:.1f}ms\n"
        
        return report


class PrivacyNotice:
    """Generate and display privacy notice for telemetry"""
    
    @staticmethod
    def get_notice() -> str:
        return """
QTM3 Telemetry Notice
====================

This software collects anonymous usage metrics to improve the user experience.

What we collect:
✓ Performance metrics (latency, throughput)
✓ Feature usage counts
✓ Error types (no error messages)
✓ Session identifiers (hashed, not linked to you)

What we DON'T collect:
✗ Task content or titles
✗ File paths or project names
✗ Personal information
✗ IP addresses or location

All data stays local in ~/qtm3/telemetry.db
You can delete this file anytime to remove all metrics.

To opt out completely:
  export QTM3_TELEMETRY=off
"""
    
    @staticmethod
    def check_consent() -> bool:
        """Check if user has consented to telemetry"""
        if os.environ.get('QTM3_TELEMETRY') == 'off':
            return False
        
        consent_file = Path.home() / "qtm3" / ".telemetry_consent"
        if consent_file.exists():
            return consent_file.read_text().strip() == 'yes'
        
        # First run - ask for consent
        print(PrivacyNotice.get_notice())
        response = input("\nEnable anonymous telemetry? (y/N): ")
        
        consent = response.lower() == 'y'
        consent_file.parent.mkdir(exist_ok=True)
        consent_file.write_text('yes' if consent else 'no')
        
        return consent


# Integration with main application
class TelemetryMixin:
    """Mixin for adding telemetry to QTM3 components"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telemetry = None
        if PrivacyNotice.check_consent():
            self.telemetry = TelemetryLogger()
    
    def track_event(self, event_type: str, duration_ms: float = None, **kwargs):
        """Track an event if telemetry is enabled"""
        if self.telemetry:
            self.telemetry.log_event(event_type, duration_ms, kwargs)
    
    def track_metric(self, metric_name: str, value: float, unit: str = "count"):
        """Track a metric if telemetry is enabled"""
        if self.telemetry:
            self.telemetry.log_metric(metric_name, value, unit)


if __name__ == "__main__":
    # Generate weekly report
    logger = TelemetryLogger()
    print(logger.generate_weekly_report())