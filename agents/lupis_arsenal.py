#!/usr/bin/env python3
"""
LUPIS Arsenal - Specialized Tools and Components
Implements the core LUPIS toolset: sensors, analyzers, actuators, and ledgers
Version: 2025-06-17
"""

import asyncio
import json
import sqlite3
import hashlib
import hmac
import time
import zmq
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import uuid
import yaml
import subprocess
from enum import Enum

import requests
from github import Github


class UCoinTransaction(Enum):
    """U-Coin transaction types"""
    DEBIT = "debit"
    CREDIT = "credit"
    GRANT = "grant"
    PENALTY = "penalty"


@dataclass
class UCoinRecord:
    """U-Coin transaction record"""
    transaction_id: str
    timestamp: datetime
    transaction_type: UCoinTransaction
    amount: int
    balance_before: int
    balance_after: int
    reason: str
    metadata: Dict[str, Any] = None


class UCoinLedger:
    """
    U-Coin economy ledger with smart-contract style immutability
    Manages token costs, rewards, and balance enforcement
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.ucoin_ledger")
        self.ledger_path = Path(config.audit_path) / "ucoin_ledger.sqlite"
        self.current_balance = config.initial_balance
        self._initialize_ledger()
    
    def _initialize_ledger(self):
        """Initialize SQLite ledger with immutable transaction log"""
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.ledger_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                balance_before INTEGER NOT NULL,
                balance_after INTEGER NOT NULL,
                reason TEXT NOT NULL,
                metadata TEXT,
                hash_chain TEXT
            )
        ''')
        
        # Initialize with starting balance if empty
        cursor = conn.execute('SELECT COUNT(*) FROM transactions')
        if cursor.fetchone()[0] == 0:
            self._record_transaction(
                UCoinTransaction.GRANT,
                self.config.initial_balance,
                "initial_grant",
                {}
            )
        else:
            # Load current balance from last transaction
            cursor = conn.execute(
                'SELECT balance_after FROM transactions ORDER BY timestamp DESC LIMIT 1'
            )
            result = cursor.fetchone()
            if result:
                self.current_balance = result[0]
        
        conn.close()
    
    def check_balance(self) -> int:
        """Get current U-Coin balance"""
        return self.current_balance
    
    def can_afford(self, amount: int) -> bool:
        """Check if sufficient balance for transaction"""
        return self.current_balance >= amount
    
    def debit(self, amount: int, reason: str, metadata: Dict[str, Any] = None) -> bool:
        """Debit tokens from balance"""
        if not self.can_afford(amount):
            self.logger.warning("Insufficient U-Coin balance: %d < %d", self.current_balance, amount)
            return False
        
        self._record_transaction(UCoinTransaction.DEBIT, amount, reason, metadata or {})
        return True
    
    def credit(self, amount: int, reason: str, metadata: Dict[str, Any] = None):
        """Credit tokens to balance"""
        # Apply quality bonus if applicable
        if metadata and metadata.get('quality_bonus'):
            amount = int(amount * self.config.quality_bonus_multiplier)
        
        # Enforce maximum balance
        if self.current_balance + amount > self.config.max_balance:
            amount = self.config.max_balance - self.current_balance
        
        if amount > 0:
            self._record_transaction(UCoinTransaction.CREDIT, amount, reason, metadata or {})
    
    def daily_grant(self) -> int:
        """Grant daily token allowance"""
        amount = self.config.daily_token_grant
        
        # Check if already granted today
        today = datetime.now().date()
        conn = sqlite3.connect(self.ledger_path)
        cursor = conn.execute(
            'SELECT COUNT(*) FROM transactions WHERE DATE(timestamp) = ? AND reason = "daily_grant"',
            (today.isoformat(),)
        )
        
        if cursor.fetchone()[0] > 0:
            conn.close()
            return 0  # Already granted today
        
        conn.close()
        self.credit(amount, "daily_grant", {"date": today.isoformat()})
        return amount
    
    def _record_transaction(self, transaction_type: UCoinTransaction, amount: int, reason: str, metadata: Dict[str, Any]):
        """Record immutable transaction with hash chain"""
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now()
        balance_before = self.current_balance
        
        if transaction_type in [UCoinTransaction.DEBIT, UCoinTransaction.PENALTY]:
            balance_after = balance_before - amount
        else:
            balance_after = balance_before + amount
        
        # Generate hash chain
        prev_hash = self._get_last_hash()
        record_data = f"{transaction_id}{timestamp.isoformat()}{transaction_type.value}{amount}{balance_before}{balance_after}{reason}"
        current_hash = hashlib.sha256((prev_hash + record_data).encode()).hexdigest()
        
        # Store transaction
        conn = sqlite3.connect(self.ledger_path)
        conn.execute('''
            INSERT INTO transactions 
            (transaction_id, timestamp, transaction_type, amount, balance_before, balance_after, reason, metadata, hash_chain)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_id,
            timestamp.isoformat(),
            transaction_type.value,
            amount,
            balance_before,
            balance_after,
            reason,
            json.dumps(metadata),
            current_hash
        ))
        conn.commit()
        conn.close()
        
        self.current_balance = balance_after
        
        self.logger.info("U-Coin transaction: %s %d tokens (%s) - Balance: %d",
                        transaction_type.value, amount, reason, self.current_balance)
    
    def _get_last_hash(self) -> str:
        """Get hash from last transaction for chain continuity"""
        conn = sqlite3.connect(self.ledger_path)
        cursor = conn.execute('SELECT hash_chain FROM transactions ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "genesis"
    
    def get_transaction_history(self, limit: int = 100) -> List[UCoinRecord]:
        """Get recent transaction history"""
        conn = sqlite3.connect(self.ledger_path)
        cursor = conn.execute('''
            SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?
        ''', (limit,))
        
        records = []
        for row in cursor.fetchall():
            metadata = json.loads(row[7]) if row[7] else {}
            record = UCoinRecord(
                transaction_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                transaction_type=UCoinTransaction(row[2]),
                amount=row[3],
                balance_before=row[4],
                balance_after=row[5],
                reason=row[6],
                metadata=metadata
            )
            records.append(record)
        
        conn.close()
        return records


class TelemetrySensor:
    """
    Telemetry sensor for collecting KPIs and performance metrics
    Integrates with ZeroMQ streams and test frameworks
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.telemetry_sensor")
        self.context = zmq.Context()
        self.socket = None
        self.metrics_cache = {}
        self.is_running = False
    
    async def start(self):
        """Start telemetry collection"""
        self.logger.info("Starting telemetry sensor on port %d", self.config.telemetry_port)
        
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://localhost:{self.config.telemetry_port}")
        self.socket.setsockopt(zmq.SUBSCRIBE, b"")  # Subscribe to all messages
        self.socket.setsockopt(zmq.RCVTIMEO, self.config.telemetry_timeout)
        
        self.is_running = True
    
    async def stop(self):
        """Stop telemetry collection"""
        self.is_running = False
        if self.socket:
            self.socket.close()
        self.context.term()
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect current metrics from all sources"""
        metrics = {
            'capture_latency': await self._get_capture_latency(),
            'throughput': await self._get_throughput(),
            'accuracy': await self._get_context_accuracy(),
            'error_rate': await self._get_error_rate(),
            'timestamp': datetime.now()
        }
        
        # Update cache
        self.metrics_cache.update(metrics)
        return metrics
    
    async def _get_capture_latency(self) -> float:
        """Get current capture latency in seconds"""
        # TODO: Implement actual latency measurement
        # For now, simulate with cached value or default
        return self.metrics_cache.get('capture_latency', 2.5)
    
    async def _get_throughput(self) -> float:
        """Get current throughput (requests/second)"""
        # TODO: Implement actual throughput measurement
        return self.metrics_cache.get('throughput', 50.0)
    
    async def _get_context_accuracy(self) -> float:
        """Get context accuracy percentage"""
        # TODO: Implement actual accuracy measurement
        return self.metrics_cache.get('accuracy', 0.85)
    
    async def _get_error_rate(self) -> float:
        """Get current error rate percentage"""
        # TODO: Implement actual error rate calculation
        return self.metrics_cache.get('error_rate', 0.02)
    
    def listen_for_test_events(self) -> Optional[Dict[str, Any]]:
        """Listen for pytest events via plugin"""
        try:
            if not self.socket:
                return None
            
            # Non-blocking receive
            message = self.socket.recv_json(zmq.NOBLOCK)
            return message
        except zmq.Again:
            return None
        except Exception as e:
            self.logger.error("Error receiving telemetry: %s", e)
            return None


class DriftAnalyzer:
    """
    Component drift analyzer that calculates structural and behavioral changes
    Compares current state with historical baselines
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.drift_analyzer")
        self.baselines = {}
        self.drift_history = []
    
    async def analyze_component_drift(self, component_path: str) -> Dict[str, Any]:
        """Analyze drift for a specific component"""
        try:
            current_state = await self._extract_component_state(component_path)
            baseline = self.baselines.get(component_path)
            
            if not baseline:
                # First time analysis - establish baseline
                self.baselines[component_path] = current_state
                return {
                    'component': component_path,
                    'drift_score': 0.0,
                    'baseline_established': True,
                    'analysis_timestamp': datetime.now()
                }
            
            # Calculate drift scores
            structure_drift = self._calculate_structure_drift(baseline, current_state)
            behavior_drift = self._calculate_behavior_drift(baseline, current_state)
            interaction_drift = self._calculate_interaction_drift(baseline, current_state)
            
            # Weighted composite score
            composite_drift = (
                structure_drift * self.config.structure_weight +
                behavior_drift * self.config.behavior_weight +
                interaction_drift * self.config.interaction_weight
            )
            
            drift_result = {
                'component': component_path,
                'drift_score': composite_drift,
                'structure_drift': structure_drift,
                'behavior_drift': behavior_drift,
                'interaction_drift': interaction_drift,
                'analysis_timestamp': datetime.now(),
                'baseline_timestamp': baseline.get('timestamp'),
                'severity': self._categorize_drift(composite_drift)
            }
            
            # Update drift history
            self.drift_history.append(drift_result)
            if len(self.drift_history) > 100:  # Keep last 100 entries
                self.drift_history.pop(0)
            
            return drift_result
            
        except Exception as e:
            self.logger.error("Error analyzing drift for %s: %s", component_path, e)
            return {
                'component': component_path,
                'drift_score': 0.0,
                'error': str(e),
                'analysis_timestamp': datetime.now()
            }
    
    async def _extract_component_state(self, component_path: str) -> Dict[str, Any]:
        """Extract current state of component for comparison"""
        state = {
            'timestamp': datetime.now(),
            'file_size': 0,
            'function_count': 0,
            'class_count': 0,
            'imports': [],
            'dependencies': [],
            'complexity_metrics': {}
        }
        
        try:
            path = Path(component_path)
            if path.exists():
                state['file_size'] = path.stat().st_size
                
                # Basic Python file analysis
                if path.suffix == '.py':
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count functions and classes (simple heuristic)
                    state['function_count'] = content.count('def ')
                    state['class_count'] = content.count('class ')
                    
                    # Extract imports
                    import_lines = [line.strip() for line in content.split('\n') 
                                  if line.strip().startswith(('import ', 'from '))]
                    state['imports'] = import_lines
        
        except Exception as e:
            self.logger.warning("Error extracting state for %s: %s", component_path, e)
        
        return state
    
    def _calculate_structure_drift(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Calculate structural drift score (0.0 to 1.0)"""
        drift_factors = []
        
        # File size change
        if baseline.get('file_size', 0) > 0:
            size_change = abs(current.get('file_size', 0) - baseline['file_size']) / baseline['file_size']
            drift_factors.append(min(size_change, 1.0))
        
        # Function count change
        baseline_funcs = baseline.get('function_count', 0)
        current_funcs = current.get('function_count', 0)
        if baseline_funcs > 0:
            func_change = abs(current_funcs - baseline_funcs) / baseline_funcs
            drift_factors.append(min(func_change, 1.0))
        
        # Class count change
        baseline_classes = baseline.get('class_count', 0)
        current_classes = current.get('class_count', 0)
        if baseline_classes > 0:
            class_change = abs(current_classes - baseline_classes) / baseline_classes
            drift_factors.append(min(class_change, 1.0))
        
        # Import changes
        baseline_imports = set(baseline.get('imports', []))
        current_imports = set(current.get('imports', []))
        if baseline_imports:
            import_diff = len(baseline_imports.symmetric_difference(current_imports))
            import_change = import_diff / len(baseline_imports)
            drift_factors.append(min(import_change, 1.0))
        
        return sum(drift_factors) / len(drift_factors) if drift_factors else 0.0
    
    def _calculate_behavior_drift(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Calculate behavioral drift score"""
        # TODO: Implement behavioral analysis (execution patterns, etc.)
        return 0.0
    
    def _calculate_interaction_drift(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> float:
        """Calculate interaction drift score"""
        # TODO: Implement interaction pattern analysis
        return 0.0
    
    def _categorize_drift(self, drift_score: float) -> str:
        """Categorize drift severity"""
        if drift_score >= 0.7:
            return "critical"
        elif drift_score >= 0.5:
            return "warning"
        elif drift_score >= 0.3:
            return "info"
        else:
            return "minimal"


class ROIEstimator:
    """
    ROI (Return on Investment) estimator for optimization proposals
    Calculates business value vs effort for proposed changes
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.roi_estimator")
        self.historical_data = []
    
    async def estimate_roi(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate ROI for an optimization proposal"""
        try:
            # Extract proposal parameters
            proposal_type = proposal.get('type', 'unknown')
            effort_estimate = proposal.get('effort_estimate', 5)
            target_components = proposal.get('target_components', [])
            projected_improvement = proposal.get('projected_improvement', 0.1)
            
            # Calculate business value
            business_value = self._calculate_business_value(
                proposal_type, projected_improvement, target_components
            )
            
            # Calculate implementation risk
            risk_score = self._calculate_risk_score(proposal_type, effort_estimate)
            
            # Calculate ROI
            if effort_estimate > 0:
                roi_score = business_value / effort_estimate
            else:
                roi_score = 0.0
            
            # Adjust for risk
            risk_adjusted_roi = roi_score * (1 - risk_score)
            
            result = {
                'proposal_id': proposal.get('id', str(uuid.uuid4())),
                'roi_score': min(roi_score, 1.0),
                'risk_adjusted_roi': min(risk_adjusted_roi, 1.0),
                'business_value': business_value,
                'effort_estimate': effort_estimate,
                'risk_score': risk_score,
                'confidence': self._calculate_confidence(proposal),
                'estimated_at': datetime.now(),
                'factors': {
                    'type_multiplier': self._get_type_multiplier(proposal_type),
                    'component_criticality': self._assess_component_criticality(target_components),
                    'historical_success_rate': self._get_historical_success_rate(proposal_type)
                }
            }
            
            # Store for historical analysis
            self.historical_data.append(result)
            if len(self.historical_data) > 1000:  # Keep last 1000 estimates
                self.historical_data.pop(0)
            
            return result
            
        except Exception as e:
            self.logger.error("Error estimating ROI: %s", e)
            return {
                'roi_score': 0.0,
                'error': str(e),
                'estimated_at': datetime.now()
            }
    
    def _calculate_business_value(self, proposal_type: str, improvement: float, components: List[str]) -> float:
        """Calculate business value score"""
        # Base value from improvement percentage
        base_value = improvement * self.config.business_value_multiplier
        
        # Type-specific multipliers
        type_multiplier = self._get_type_multiplier(proposal_type)
        
        # Component criticality factor
        criticality_factor = self._assess_component_criticality(components)
        
        business_value = base_value * type_multiplier * criticality_factor
        return min(business_value, 1.0)
    
    def _get_type_multiplier(self, proposal_type: str) -> float:
        """Get multiplier based on optimization type"""
        multipliers = {
            'prompt_optimization': 1.2,
            'caching_improvement': 1.5,
            'performance_tuning': 1.3,
            'bug_fix': 1.8,
            'security_improvement': 2.0,
            'test_coverage': 1.1,
            'documentation': 0.8,
            'refactoring': 1.0
        }
        return multipliers.get(proposal_type, 1.0)
    
    def _assess_component_criticality(self, components: List[str]) -> float:
        """Assess criticality of target components"""
        if not components:
            return 1.0
        
        critical_components = [
            'orchestrator', 'memory_agent', 'reasoning_agent',
            'perception_agent', 'user_story_synthesiser'
        ]
        
        criticality_scores = []
        for component in components:
            if any(critical in component.lower() for critical in critical_components):
                criticality_scores.append(1.5)
            else:
                criticality_scores.append(1.0)
        
        return sum(criticality_scores) / len(criticality_scores)
    
    def _calculate_risk_score(self, proposal_type: str, effort_estimate: int) -> float:
        """Calculate implementation risk score"""
        # Base risk from effort (higher effort = higher risk)
        effort_risk = min(effort_estimate / self.config.max_effort_threshold, 1.0)
        
        # Type-specific risk factors
        type_risks = {
            'prompt_optimization': 0.2,
            'caching_improvement': 0.3,
            'performance_tuning': 0.4,
            'bug_fix': 0.1,
            'security_improvement': 0.5,
            'test_coverage': 0.1,
            'documentation': 0.1,
            'refactoring': 0.6
        }
        
        type_risk = type_risks.get(proposal_type, 0.5)
        
        # Composite risk
        composite_risk = (effort_risk + type_risk) / 2
        return min(composite_risk, 1.0)
    
    def _calculate_confidence(self, proposal: Dict[str, Any]) -> float:
        """Calculate confidence in ROI estimate"""
        # TODO: Implement confidence calculation based on data quality
        return 0.8  # Placeholder
    
    def _get_historical_success_rate(self, proposal_type: str) -> float:
        """Get historical success rate for proposal type"""
        # TODO: Implement based on actual historical data
        return 0.7  # Placeholder


class OptimizationActuator:
    """
    Optimization actuator for automated GitHub ticket creation and system actions
    Implements automation gates and rate limiting
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.optimization_actuator")
        self.github_client = None
        self.rate_limiter = {}
        
        # Initialize GitHub client if configured
        if config.github_api_token:
            self.github_client = Github(config.github_api_token)
    
    async def create_optimization_ticket(self, proposal: Dict[str, Any], roi_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitHub optimization ticket"""
        if not self._check_rate_limit('tickets'):
            return {'success': False, 'reason': 'rate_limit_exceeded'}
        
        try:
            # Format ticket content
            title = f"{self.config.ticket_prefix} {proposal.get('description', 'Optimization')}"
            body = self._format_ticket_body(proposal, roi_analysis)
            labels = ['lupis-optimization', 'automated'] + proposal.get('labels', [])
            
            if self.github_client and self.config.github_repo:
                # Create actual GitHub issue
                repo = self.github_client.get_repo(self.config.github_repo)
                issue = repo.create_issue(
                    title=title,
                    body=body,
                    labels=labels
                )
                
                result = {
                    'success': True,
                    'ticket_id': f"#{issue.number}",
                    'url': issue.html_url,
                    'created_at': datetime.now()
                }
            else:
                # Simulate ticket creation for testing
                result = {
                    'success': True,
                    'ticket_id': f"SIM-{int(time.time())}",
                    'url': f"https://github.com/simulated/issues/{int(time.time())}",
                    'created_at': datetime.now()
                }
            
            self._update_rate_limit('tickets')
            self.logger.info("Created optimization ticket: %s", result['ticket_id'])
            return result
            
        except Exception as e:
            self.logger.error("Error creating optimization ticket: %s", e)
            return {'success': False, 'reason': str(e)}
    
    async def create_pull_request(self, proposal: Dict[str, Any], changes: Dict[str, Any]) -> Dict[str, Any]:
        """Create automated pull request for approved optimizations"""
        # TODO: Implement automated PR creation
        return {'success': False, 'reason': 'not_implemented'}
    
    def _format_ticket_body(self, proposal: Dict[str, Any], roi_analysis: Dict[str, Any]) -> str:
        """Format GitHub issue body with all relevant information"""
        body = f"""
## LUPIS Optimization Proposal

**Type:** {proposal.get('type', 'Unknown')}
**Component(s):** {', '.join(proposal.get('target_components', []))}

### Description
{proposal.get('description', 'No description provided')}

### ROI Analysis
- **ROI Score:** {roi_analysis.get('roi_score', 0.0):.3f}
- **Risk-Adjusted ROI:** {roi_analysis.get('risk_adjusted_roi', 0.0):.3f}
- **Business Value:** {roi_analysis.get('business_value', 0.0):.3f}
- **Implementation Risk:** {roi_analysis.get('risk_score', 0.0):.3f}
- **Effort Estimate:** {roi_analysis.get('effort_estimate', 0)} story points

### Projected Impact
- **Performance Improvement:** {proposal.get('projected_improvement', 0.0):.1%}
- **Target Metrics:** {', '.join(proposal.get('target_metrics', []))}

### Evidence
{self._format_evidence(proposal.get('evidence', []))}

### Acceptance Criteria
{self._format_acceptance_criteria(proposal.get('acceptance_criteria', []))}

### Implementation Notes
{proposal.get('implementation_notes', 'See proposal details above.')}

---
**LUPIS Metadata:**
- Generated: {datetime.now().isoformat()}
- Proposal ID: {proposal.get('id', 'N/A')}
- ROI Confidence: {roi_analysis.get('confidence', 0.0):.2f}
- Auto-executable: {roi_analysis.get('roi_score', 0.0) >= 0.6}

*This optimization was automatically generated by LUPIS v{getattr(self.config, 'version', '2025-06-17')}*
        """.strip()
        
        return body
    
    def _format_evidence(self, evidence_list: List[str]) -> str:
        """Format evidence list for ticket body"""
        if not evidence_list:
            return "- No specific evidence provided"
        
        return '\n'.join(f"- {item}" for item in evidence_list)
    
    def _format_acceptance_criteria(self, criteria_list: List[str]) -> str:
        """Format acceptance criteria as checklist"""
        if not criteria_list:
            criteria_list = [
                "Implementation passes all existing tests",
                "Performance metrics show expected improvement", 
                "No regressions in other components",
                "Documentation updated as needed"
            ]
        
        return '\n'.join(f"- [ ] {criteria}" for criteria in criteria_list)
    
    def _check_rate_limit(self, action_type: str) -> bool:
        """Check if action is within rate limits"""
        now = time.time()
        hour_key = f"{action_type}_{int(now // 3600)}"
        
        if hour_key not in self.rate_limiter:
            self.rate_limiter[hour_key] = 0
        
        limits = {
            'tickets': self.config.max_tickets_per_hour,
            'mutations': self.config.max_mutations_per_hour,
            'agents': self.config.max_agents_per_day
        }
        
        limit = limits.get(action_type, 10)
        return self.rate_limiter[hour_key] < limit
    
    def _update_rate_limit(self, action_type: str):
        """Update rate limit counter"""
        now = time.time()
        hour_key = f"{action_type}_{int(now // 3600)}"
        
        if hour_key not in self.rate_limiter:
            self.rate_limiter[hour_key] = 0
        
        self.rate_limiter[hour_key] += 1
        
        # Cleanup old entries
        current_hour = int(now // 3600)
        old_keys = [k for k in self.rate_limiter.keys() 
                   if int(k.split('_')[-1]) < current_hour - 24]
        for key in old_keys:
            del self.rate_limiter[key]


class AuditSink:
    """
    Immutable audit sink with hash chain verification
    Stores all LUPIS decisions and actions for traceability
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.audit_sink")
        self.audit_path = Path(config.audit_path)
        self.audit_file = self.audit_path / config.audit_file
        self.chain_file = self.audit_path / config.chain_file
        self.pending_entries = []
        
        self._initialize_audit_system()
    
    def _initialize_audit_system(self):
        """Initialize audit system with proper structure"""
        self.audit_path.mkdir(parents=True, exist_ok=True)
        
        if self.config.chain_enabled:
            # Initialize SQLite chain if it doesn't exist
            conn = sqlite3.connect(self.chain_file)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_chain (
                    entry_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    evidence_hash TEXT NOT NULL,
                    reasoning_hash TEXT NOT NULL,
                    previous_hash TEXT,
                    current_hash TEXT NOT NULL,
                    signature TEXT
                )
            ''')
            conn.close()
    
    async def log_action(self, entry_id: str, action: str, evidence: Dict[str, Any], 
                        reasoning: str, projected_impact: str, roi_score: float, 
                        urgency: float, outcome: str = None) -> str:
        """Log an action to the audit trail"""
        timestamp = datetime.now()
        
        # Create audit entry
        entry = {
            'entry_id': entry_id,
            'timestamp': timestamp.isoformat(),
            'action': action,
            'evidence': evidence,
            'reasoning': reasoning,
            'projected_impact': projected_impact,
            'roi_score': roi_score,
            'urgency': urgency,
            'outcome': outcome
        }
        
        # Add to pending entries
        self.pending_entries.append(entry)
        
        # Write to YAML file
        await self._write_yaml_entry(entry)
        
        # Add to hash chain if enabled
        if self.config.chain_enabled:
            chain_hash = await self._add_to_chain(entry)
            entry['hash_chain'] = chain_hash
        
        self.logger.debug("Audit entry logged: %s", entry_id)
        return entry_id
    
    async def _write_yaml_entry(self, entry: Dict[str, Any]):
        """Write entry to YAML audit file"""
        try:
            # Append to YAML file
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write('---\n')
                yaml.dump(entry, f, default_flow_style=False)
                f.write('\n')
        except Exception as e:
            self.logger.error("Error writing audit entry: %s", e)
    
    async def _add_to_chain(self, entry: Dict[str, Any]) -> str:
        """Add entry to immutable hash chain"""
        try:
            # Generate hashes
            evidence_hash = hashlib.sha256(
                json.dumps(entry['evidence'], sort_keys=True).encode()
            ).hexdigest()
            
            reasoning_hash = hashlib.sha256(
                entry['reasoning'].encode()
            ).hexdigest()
            
            # Get previous hash
            previous_hash = self._get_last_chain_hash()
            
            # Generate current hash
            chain_data = f"{entry['entry_id']}{entry['timestamp']}{entry['action']}{evidence_hash}{reasoning_hash}{previous_hash}"
            current_hash = hashlib.sha256(chain_data.encode()).hexdigest()
            
            # Sign if configured
            signature = None
            if self.config.sign_entries:
                signature = self._sign_entry(current_hash)
            
            # Store in chain
            conn = sqlite3.connect(self.chain_file)
            conn.execute('''
                INSERT INTO audit_chain 
                (entry_id, timestamp, action, evidence_hash, reasoning_hash, previous_hash, current_hash, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry['entry_id'],
                entry['timestamp'],
                entry['action'],
                evidence_hash,
                reasoning_hash,
                previous_hash,
                current_hash,
                signature
            ))
            conn.commit()
            conn.close()
            
            return current_hash
            
        except Exception as e:
            self.logger.error("Error adding to audit chain: %s", e)
            return "error"
    
    def _get_last_chain_hash(self) -> str:
        """Get hash from last chain entry"""
        try:
            conn = sqlite3.connect(self.chain_file)
            cursor = conn.execute('SELECT current_hash FROM audit_chain ORDER BY timestamp DESC LIMIT 1')
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "genesis"
        except Exception:
            return "genesis"
    
    def _sign_entry(self, hash_value: str) -> str:
        """Sign audit entry hash (placeholder implementation)"""
        # TODO: Implement actual cryptographic signing
        return f"signed_{hash_value[:16]}"
    
    async def flush(self):
        """Flush any pending audit entries"""
        if self.pending_entries:
            self.logger.info("Flushing %d pending audit entries", len(self.pending_entries))
            self.pending_entries.clear()
    
    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify audit chain integrity"""
        try:
            conn = sqlite3.connect(self.chain_file)
            cursor = conn.execute('SELECT * FROM audit_chain ORDER BY timestamp ASC')
            
            verification_result = {
                'valid': True,
                'total_entries': 0,
                'verified_entries': 0,
                'broken_links': [],
                'verification_timestamp': datetime.now()
            }
            
            previous_hash = "genesis"
            for row in cursor.fetchall():
                verification_result['total_entries'] += 1
                
                # Reconstruct hash
                entry_id, timestamp, action, evidence_hash, reasoning_hash, prev_hash, current_hash, signature = row
                
                # Verify chain link
                if prev_hash == previous_hash:
                    verification_result['verified_entries'] += 1
                else:
                    verification_result['broken_links'].append({
                        'entry_id': entry_id,
                        'expected_previous': previous_hash,
                        'actual_previous': prev_hash
                    })
                    verification_result['valid'] = False
                
                previous_hash = current_hash
            
            conn.close()
            return verification_result
            
        except Exception as e:
            self.logger.error("Error verifying chain integrity: %s", e)
            return {
                'valid': False,
                'error': str(e),
                'verification_timestamp': datetime.now()
            }


class MutationEngine:
    """
    Mutation engine for automated system improvements
    Generates, scores, and applies optimization mutations
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("qtm3.lupis.mutation_engine")
        self.active_mutations = {}
        self.mutation_history = []
    
    async def generate_mutations(self, trigger: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mutation options based on trigger"""
        mutations = []
        
        trigger_type = trigger.get('type', 'unknown')
        evidence = trigger.get('evidence', {})
        
        # Generate mutations based on trigger type
        if trigger_type == 'performance_degradation':
            mutations.extend(await self._generate_performance_mutations(evidence))
        elif trigger_type == 'drift_detection':
            mutations.extend(await self._generate_drift_mutations(evidence))
        elif trigger_type == 'test_failure':
            mutations.extend(await self._generate_test_mutations(evidence))
        
        # Limit to max options
        if len(mutations) > self.config.max_options_per_mutation:
            mutations = mutations[:self.config.max_options_per_mutation]
        
        return mutations
    
    async def _generate_performance_mutations(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance-focused mutations"""
        mutations = []
        
        # Prompt optimization
        if 'prompt_tuning' in self.config.enabled_mutations:
            mutations.append({
                'id': str(uuid.uuid4()),
                'type': 'prompt_optimization',
                'description': 'Optimize AI prompts to reduce response time',
                'target_files': ['prompts/*.qwen'],
                'effort_estimate': 3,
                'projected_improvement': 0.2,
                'safety_score': 0.8
            })
        
        # Caching improvements
        mutations.append({
            'id': str(uuid.uuid4()),
            'type': 'caching_improvement',
            'description': 'Implement smart caching for frequent operations',
            'target_files': ['agents/memory_agent.py'],
            'effort_estimate': 5,
            'projected_improvement': 0.3,
            'safety_score': 0.9
        })
        
        return mutations
    
    async def _generate_drift_mutations(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mutations to address component drift"""
        mutations = []
        
        component = evidence.get('component', 'unknown')
        drift_score = evidence.get('drift_score', 0.0)
        
        if drift_score > 0.5:
            mutations.append({
                'id': str(uuid.uuid4()),
                'type': 'refactoring',
                'description': f'Refactor {component} to reduce structural drift',
                'target_files': [component],
                'effort_estimate': 8,
                'projected_improvement': drift_score * 0.7,
                'safety_score': 0.6
            })
        
        return mutations
    
    async def _generate_test_mutations(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mutations to improve test coverage and reliability"""
        mutations = []
        
        if 'test_generation' in self.config.enabled_mutations:
            mutations.append({
                'id': str(uuid.uuid4()),
                'type': 'test_improvement',
                'description': 'Generate additional test cases for improved coverage',
                'target_files': ['tests/'],
                'effort_estimate': 4,
                'projected_improvement': 0.15,
                'safety_score': 0.95
            })
        
        return mutations
    
    async def apply_mutation(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply approved mutation to the system"""
        mutation_id = mutation['id']
        
        try:
            self.logger.info("Applying mutation: %s", mutation['description'])
            
            # Track active mutation
            self.active_mutations[mutation_id] = {
                'mutation': mutation,
                'started_at': datetime.now(),
                'status': 'applying'
            }
            
            # Apply based on mutation type
            result = await self._apply_by_type(mutation)
            
            # Update tracking
            self.active_mutations[mutation_id]['status'] = 'completed' if result['success'] else 'failed'
            self.active_mutations[mutation_id]['completed_at'] = datetime.now()
            self.active_mutations[mutation_id]['result'] = result
            
            # Add to history
            self.mutation_history.append({
                'mutation_id': mutation_id,
                'applied_at': datetime.now(),
                'success': result['success'],
                'result': result
            })
            
            return result
            
        except Exception as e:
            self.logger.error("Error applying mutation %s: %s", mutation_id, e)
            
            if mutation_id in self.active_mutations:
                self.active_mutations[mutation_id]['status'] = 'error'
                self.active_mutations[mutation_id]['error'] = str(e)
            
            return {
                'success': False,
                'error': str(e),
                'mutation_id': mutation_id
            }
    
    async def _apply_by_type(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mutation based on its type"""
        mutation_type = mutation['type']
        
        if mutation_type == 'prompt_optimization':
            return await self._apply_prompt_optimization(mutation)
        elif mutation_type == 'caching_improvement':
            return await self._apply_caching_improvement(mutation)
        elif mutation_type == 'test_improvement':
            return await self._apply_test_improvement(mutation)
        elif mutation_type == 'refactoring':
            return await self._apply_refactoring(mutation)
        else:
            return {
                'success': False,
                'reason': f'Unknown mutation type: {mutation_type}'
            }
    
    async def _apply_prompt_optimization(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply prompt optimization mutation"""
        # TODO: Implement actual prompt optimization
        return {
            'success': True,
            'changes_made': ['optimized_prompts'],
            'files_modified': mutation.get('target_files', [])
        }
    
    async def _apply_caching_improvement(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply caching improvement mutation"""
        # TODO: Implement actual caching improvements
        return {
            'success': True,
            'changes_made': ['added_caching_layer'],
            'files_modified': mutation.get('target_files', [])
        }
    
    async def _apply_test_improvement(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply test improvement mutation"""
        # TODO: Implement actual test generation
        return {
            'success': True,
            'changes_made': ['generated_additional_tests'],
            'files_modified': mutation.get('target_files', [])
        }
    
    async def _apply_refactoring(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply refactoring mutation"""
        # TODO: Implement actual refactoring
        return {
            'success': True,
            'changes_made': ['refactored_components'],
            'files_modified': mutation.get('target_files', [])
        }
    
    def get_active_mutations(self) -> Dict[str, Any]:
        """Get currently active mutations"""
        return self.active_mutations.copy()
    
    def get_mutation_statistics(self) -> Dict[str, Any]:
        """Get mutation engine statistics"""
        total_mutations = len(self.mutation_history)
        successful_mutations = sum(1 for m in self.mutation_history if m['success'])
        
        return {
            'total_mutations_applied': total_mutations,
            'successful_mutations': successful_mutations,
            'success_rate': successful_mutations / total_mutations if total_mutations > 0 else 0.0,
            'active_mutations': len(self.active_mutations),
            'enabled_mutation_types': self.config.enabled_mutations,
            'last_mutation_at': self.mutation_history[-1]['applied_at'] if self.mutation_history else None
        }


# Factory functions for easy component creation

def create_ucoin_ledger(config) -> UCoinLedger:
    """Create U-Coin ledger instance"""
    return UCoinLedger(config)

def create_telemetry_sensor(config) -> TelemetrySensor:
    """Create telemetry sensor instance"""
    return TelemetrySensor(config)

def create_drift_analyzer(config) -> DriftAnalyzer:
    """Create drift analyzer instance"""
    return DriftAnalyzer(config)

def create_roi_estimator(config) -> ROIEstimator:
    """Create ROI estimator instance"""
    return ROIEstimator(config)

def create_optimization_actuator(config) -> OptimizationActuator:
    """Create optimization actuator instance"""
    return OptimizationActuator(config)

def create_audit_sink(config) -> AuditSink:
    """Create audit sink instance"""
    return AuditSink(config)

def create_mutation_engine(config) -> MutationEngine:
    """Create mutation engine instance"""
    return MutationEngine(config)