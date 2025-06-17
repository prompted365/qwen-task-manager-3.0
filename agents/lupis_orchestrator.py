#!/usr/bin/env python3
"""
LUPIS (Loop-Updating Perception-Intelligence Synthesiser) Orchestrator
Main orchestrator that closes the learning loop across Perception → Memory → Reasoning → Exchange → Interface
Version: 2025-06-17
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import hashlib

from config.lupis_config import LUPISConfig, get_lupis_config, AutomationGate


@dataclass
class MetricEvent:
    """Metric event structure"""
    metric: str
    value: float
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = None


@dataclass
class DriftReport:
    """Component drift report structure"""
    component: str
    score: float
    evidence: Dict[str, Any]
    timestamp: datetime
    severity: str = "info"


@dataclass
class UserFeedback:
    """User feedback structure"""
    session_id: str
    sentiment: str
    note: str
    timestamp: datetime
    metadata: Dict[str, Any] = None


@dataclass
class OptimizationTicket:
    """Optimization ticket structure"""
    ticket_id: str
    title: str
    description: str
    evidence: List[str]
    roi_score: float
    urgency: float
    effort_estimate: int
    acceptance_criteria: List[str]
    labels: List[str]
    timestamp: datetime


@dataclass
class AuditEntry:
    """Audit log entry structure"""
    entry_id: str
    timestamp: datetime
    action: str
    evidence: Dict[str, Any]
    reasoning: str
    projected_impact: str
    roi_score: float
    urgency: float
    outcome: Optional[str] = None
    hash_chain: Optional[str] = None


class LUPISOrchestrator:
    """
    Main LUPIS orchestrator that implements the continuous learning loop:
    LISTEN → ASSESS → SYNTHESISE → SCORE → EMIT → LOG
    """
    
    def __init__(self, config: LUPISConfig = None):
        self.config = config or get_lupis_config()
        self.logger = self._setup_logging()
        
        # Initialize arsenal components
        self.ucoin_ledger = None
        self.telemetry_sensor = None
        self.drift_analyzer = None
        self.roi_estimator = None
        self.optimization_actuator = None
        self.audit_sink = None
        self.mutation_engine = None
        
        # State tracking
        self.running = False
        self.last_kpi_check = datetime.now()
        self.last_drift_check = datetime.now()
        self.consecutive_failures = 0
        
        # Event queues
        self.metric_queue = asyncio.Queue()
        self.drift_queue = asyncio.Queue()
        self.feedback_queue = asyncio.Queue()
        
        # Performance tracking
        self.kpi_history = []
        self.processed_events = 0
        self.optimization_tickets_created = 0
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for LUPIS orchestrator"""
        logger = logging.getLogger("qtm3.lupis_orchestrator")
        logger.setLevel(logging.DEBUG if self.config.debug_mode else logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.config.audit.audit_path).parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler
        handler = logging.FileHandler(log_dir / "lupis.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def start(self):
        """Start the LUPIS orchestrator"""
        self.logger.info("Starting LUPIS Orchestrator v%s", self.config.version)
        
        # Validate configuration
        config_errors = self.config.validate()
        if config_errors:
            self.logger.error("Configuration validation failed: %s", config_errors)
            raise ValueError(f"Invalid configuration: {config_errors}")
        
        # Initialize components (placeholder until arsenal is implemented)
        await self._initialize_components()
        
        # Start main loop
        self.running = True
        
        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self._main_loop()),
            asyncio.create_task(self._event_processor()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._periodic_tasks())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error("LUPIS orchestrator error: %s", e, exc_info=True)
            raise
        finally:
            self.running = False
    
    async def stop(self):
        """Stop the LUPIS orchestrator"""
        self.logger.info("Stopping LUPIS Orchestrator")
        self.running = False
        
        # Cleanup components
        if self.audit_sink:
            await self.audit_sink.flush()
    
    async def _initialize_components(self):
        """Initialize LUPIS arsenal components"""
        self.logger.info("Initializing LUPIS components")
        
        try:
            # Initialize U-Coin ledger
            self.ucoin_ledger = create_ucoin_ledger(self.config.ucoin)
            self.logger.info("U-Coin ledger initialized with balance: %d",
                           self.ucoin_ledger.check_balance())
            
            # Initialize telemetry sensor
            self.telemetry_sensor = create_telemetry_sensor(self.config.sensors)
            await self.telemetry_sensor.start()
            
            # Initialize analyzers
            self.drift_analyzer = create_drift_analyzer(self.config.analyzers)
            self.roi_estimator = create_roi_estimator(self.config.analyzers)
            
            # Initialize actuator
            self.optimization_actuator = create_optimization_actuator(self.config.actuators)
            
            # Initialize audit sink
            self.audit_sink = create_audit_sink(self.config.audit)
            
            # Initialize mutation engine
            self.mutation_engine = create_mutation_engine(self.config.mutation)
            
            self.logger.info("All LUPIS components initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize LUPIS components: %s", e)
            raise
    
    async def _main_loop(self):
        """Main LUPIS loop: LISTEN → ASSESS → SYNTHESISE → SCORE → EMIT → LOG"""
        self.logger.info("Starting main LUPIS loop")
        
        while self.running:
            try:
                # 1. LISTEN - Check for new events and metrics
                await self._listen_phase()
                
                # 2. ASSESS - Evaluate current state
                assessment = await self._assess_phase()
                
                # 3. SYNTHESISE - Generate optimization options if needed
                if assessment['needs_optimization']:
                    options = await self._synthesise_phase(assessment)
                    
                    # 4. SCORE - Calculate ROI and risk for options
                    scored_options = await self._score_phase(options)
                    
                    # 5. EMIT - Create tickets or alerts
                    await self._emit_phase(scored_options)
                
                # 6. LOG - Audit trail
                await self._log_phase(assessment)
                
                # Sleep between cycles
                await asyncio.sleep(self.config.sensors.kpi_poll_interval)
                
            except Exception as e:
                self.logger.error("Error in main loop: %s", e, exc_info=True)
                self.consecutive_failures += 1
                
                if self.consecutive_failures >= self.config.monitoring.alert_on_consecutive_failures:
                    await self._escalate_critical_error(e)
                
                await asyncio.sleep(10)  # Brief pause before retry
    
    async def _listen_phase(self) -> Dict[str, Any]:
        """Phase 1: LISTEN - Collect metrics, drift reports, and feedback"""
        events = {
            'metrics': [],
            'drift_reports': [],
            'feedback': [],
            'timestamp': datetime.now()
        }
        
        # Collect metric events (non-blocking)
        try:
            while not self.metric_queue.empty():
                metric_event = await asyncio.wait_for(
                    self.metric_queue.get(), 
                    timeout=0.1
                )
                events['metrics'].append(metric_event)
        except asyncio.TimeoutError:
            pass
        
        # Collect drift reports
        try:
            while not self.drift_queue.empty():
                drift_report = await asyncio.wait_for(
                    self.drift_queue.get(),
                    timeout=0.1
                )
                events['drift_reports'].append(drift_report)
        except asyncio.TimeoutError:
            pass
        
        # Collect user feedback
        try:
            while not self.feedback_queue.empty():
                feedback = await asyncio.wait_for(
                    self.feedback_queue.get(),
                    timeout=0.1
                )
                events['feedback'].append(feedback)
        except asyncio.TimeoutError:
            pass
        
        self.processed_events += len(events['metrics']) + len(events['drift_reports']) + len(events['feedback'])
        
        return events
    
    async def _assess_phase(self) -> Dict[str, Any]:
        """Phase 2: ASSESS - Evaluate KPIs and determine if optimization is needed"""
        assessment = {
            'kpi_regression': 0.0,
            'max_drift_score': 0.0,
            'needs_optimization': False,
            'urgency': 0.0,
            'triggers': [],
            'timestamp': datetime.now()
        }
        
        # TODO: Implement actual KPI assessment when components are ready
        # For now, simulate assessment logic
        
        # Check if time for periodic drift assessment
        time_since_drift_check = datetime.now() - self.last_drift_check
        if time_since_drift_check.seconds >= self.config.sensors.drift_check_interval:
            self.last_drift_check = datetime.now()
            # TODO: Trigger drift analysis
        
        # Determine if optimization is needed
        roi_threshold = self.config.analyzers.roi_threshold
        urgency_threshold = self.config.analyzers.urgency_threshold
        
        if assessment['kpi_regression'] > 0.1 or assessment['max_drift_score'] > 0.5:
            assessment['needs_optimization'] = True
            assessment['urgency'] = max(
                assessment['kpi_regression'],
                assessment['max_drift_score']
            )
            assessment['triggers'].append('performance_degradation')
        
        return assessment
    
    async def _synthesise_phase(self, assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Phase 3: SYNTHESISE - Generate optimization options"""
        options = []
        
        # Use mutation engine to generate optimization options
        options = []
        
        if self.mutation_engine:
            try:
                trigger_data = {
                    'type': 'performance_degradation' if 'performance_degradation' in assessment['triggers'] else 'general',
                    'evidence': assessment,
                    'urgency': assessment['urgency']
                }
                
                mutations = await self.mutation_engine.generate_mutations(trigger_data)
                options.extend(mutations)
                
            except Exception as e:
                self.logger.error("Error generating mutations: %s", e)
        
        if 'performance_degradation' in assessment['triggers']:
            options.append({
                'type': 'prompt_optimization',
                'description': 'Optimize model prompts to reduce latency',
                'effort_estimate': 3,
                'target_components': ['reasoning_agent'],
                'projected_improvement': 0.2
            })
            
            options.append({
                'type': 'caching_improvement',
                'description': 'Implement response caching for frequent queries',
                'effort_estimate': 5,
                'target_components': ['memory_agent'],
                'projected_improvement': 0.3
            })
        
        self.logger.debug("Generated %d optimization options", len(options))
        return options
    
    async def _score_phase(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Phase 4: SCORE - Calculate ROI and risk for optimization options"""
        scored_options = []
        
        for option in options:
            if self.roi_estimator:
                try:
                    # Use ROI estimator for proper scoring
                    roi_analysis = await self.roi_estimator.estimate_roi(option)
                    
                    scored_option = {
                        **option,
                        'roi_score': roi_analysis.get('roi_score', 0.0),
                        'risk_score': roi_analysis.get('risk_score', 0.5),
                        'composite_score': roi_analysis.get('risk_adjusted_roi', 0.0),
                        'roi_analysis': roi_analysis
                    }
                    
                except Exception as e:
                    self.logger.error("Error scoring option %s: %s", option.get('id', 'unknown'), e)
                    # Fallback to simple scoring
                    effort = option.get('effort_estimate', 5)
                    improvement = option.get('projected_improvement', 0.1)
                    roi_score = min(improvement / effort * self.config.analyzers.business_value_multiplier, 1.0)
                    
                    scored_option = {
                        **option,
                        'roi_score': roi_score,
                        'risk_score': min(effort / 10.0, 1.0),
                        'composite_score': roi_score * 0.5
                    }
            else:
                # Fallback scoring when estimator not available
                effort = option.get('effort_estimate', 5)
                improvement = option.get('projected_improvement', 0.1)
                roi_score = min(improvement / effort * self.config.analyzers.business_value_multiplier, 1.0)
                
                scored_option = {
                    **option,
                    'roi_score': roi_score,
                    'risk_score': min(effort / 10.0, 1.0),
                    'composite_score': roi_score * 0.5
                }
            
            scored_options.append(scored_option)
        
        # Sort by composite score
        scored_options.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return scored_options
    
    async def _emit_phase(self, scored_options: List[Dict[str, Any]]):
        """Phase 5: EMIT - Create optimization tickets or alerts"""
        for option in scored_options:
            roi_score = option['roi_score']
            urgency = option.get('urgency', 0.5)
            
            # Check automation gates
            should_auto_execute = (
                self.config.autonomous_mode and
                roi_score >= self.config.analyzers.roi_threshold and
                urgency >= self.config.analyzers.urgency_threshold and
                self._check_ucoin_balance(self.config.ucoin.create_ticket_cost)
            )
            
            if should_auto_execute:
                await self._create_optimization_ticket(option)
            elif roi_score >= 0.3:  # Create proposal even if not auto-executing
                await self._create_optimization_proposal(option)
    
    async def _log_phase(self, assessment: Dict[str, Any]):
        """Phase 6: LOG - Create audit trail entry"""
        audit_entry = AuditEntry(
            entry_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            action="assessment_cycle",
            evidence=assessment,
            reasoning=f"Periodic assessment cycle completed",
            projected_impact="system_monitoring",
            roi_score=0.0,
            urgency=assessment.get('urgency', 0.0)
        )
        
        # TODO: Write to audit sink when implemented
        self.logger.debug("Audit entry created: %s", audit_entry.entry_id)
    
    async def _create_optimization_ticket(self, option: Dict[str, Any]):
        """Create GitHub optimization ticket"""
        if not self.optimization_actuator:
            self.logger.warning("Optimization actuator not available")
            return
        
        # Check U-Coin balance
        cost = self.config.ucoin.create_ticket_cost
        if not self._check_ucoin_balance(cost):
            self.logger.warning("Insufficient U-Coin balance for ticket creation")
            return
        
        try:
            # Debit U-Coins
            if self.ucoin_ledger:
                self.ucoin_ledger.debit(cost, "create_optimization_ticket", {
                    'option_id': option.get('id', 'unknown'),
                    'roi_score': option.get('roi_score', 0.0)
                })
            
            # Create ticket via actuator
            roi_analysis = option.get('roi_analysis', {})
            result = await self.optimization_actuator.create_optimization_ticket(option, roi_analysis)
            
            if result.get('success'):
                # Credit reward if successful
                if self.ucoin_ledger:
                    reward = int(self.config.ucoin.successful_ticket_reward * option.get('roi_score', 0.0))
                    if reward > 0:
                        self.ucoin_ledger.credit(reward, "successful_ticket_creation", {
                            'ticket_id': result.get('ticket_id'),
                            'roi_score': option.get('roi_score', 0.0)
                        })
                
                self.optimization_tickets_created += 1
                self.logger.info("Created optimization ticket: %s", result.get('ticket_id'))
                
                # Log to audit
                if self.audit_sink:
                    await self.audit_sink.log_action(
                        entry_id=str(uuid.uuid4()),
                        action="create_optimization_ticket",
                        evidence={'option': option, 'result': result},
                        reasoning=f"Automated ticket creation for ROI {option.get('roi_score', 0.0):.3f}",
                        projected_impact=f"Performance improvement: {option.get('projected_improvement', 0.0):.1%}",
                        roi_score=option.get('roi_score', 0.0),
                        urgency=option.get('urgency', 0.5),
                        outcome="success"
                    )
            else:
                self.logger.error("Failed to create optimization ticket: %s", result.get('reason'))
                
        except Exception as e:
            self.logger.error("Error creating optimization ticket: %s", e)
    
    async def _create_optimization_proposal(self, option: Dict[str, Any]):
        """Create optimization proposal for human review"""
        try:
            if self.audit_sink:
                await self.audit_sink.log_action(
                    entry_id=str(uuid.uuid4()),
                    action="create_optimization_proposal",
                    evidence={'option': option},
                    reasoning=f"Below auto-execution threshold, creating proposal for review",
                    projected_impact=f"Performance improvement: {option.get('projected_improvement', 0.0):.1%}",
                    roi_score=option.get('roi_score', 0.0),
                    urgency=option.get('urgency', 0.5),
                    outcome="proposal_created"
                )
            
            self.logger.info("Created optimization proposal: %s", option['description'])
            
        except Exception as e:
            self.logger.error("Error creating optimization proposal: %s", e)
    
    def _format_ticket_description(self, option: Dict[str, Any]) -> str:
        """Format ticket description with evidence and reasoning"""
        description = f"""
## Optimization Proposal

**Type:** {option['type']}
**Description:** {option['description']}

## Analysis
- **ROI Score:** {option['roi_score']:.2f}
- **Effort Estimate:** {option['effort_estimate']} story points
- **Risk Score:** {option.get('risk_score', 0.0):.2f}
- **Target Components:** {', '.join(option.get('target_components', []))}

## Projected Impact
- **Performance Improvement:** {option.get('projected_improvement', 0.0):.1%}

## Evidence
<!-- Evidence will be populated by LUPIS sensors -->

## Acceptance Criteria
- [ ] Implementation passes all existing tests
- [ ] Performance metrics show expected improvement
- [ ] No regressions in other components
- [ ] Documentation updated

---
*Generated by LUPIS v{self.config.version} at {datetime.now().isoformat()}*
        """.strip()
        
        return description
    
    def _check_ucoin_balance(self, required_amount: int = 0) -> bool:
        """Check if sufficient U-Coin balance for autonomous action"""
        if not self.ucoin_ledger:
            return False
        
        current_balance = self.ucoin_ledger.check_balance()
        min_balance = self.config.ucoin.min_balance_for_auto
        
        return current_balance >= max(required_amount, min_balance)
    
    async def _escalate_critical_error(self, error: Exception):
        """Escalate critical error to orchestrator"""
        self.logger.critical("LUPIS critical error - escalating: %s", error)
        
        # TODO: Implement escalation to main orchestrator
        
        # Reset failure counter after escalation
        self.consecutive_failures = 0
    
    async def _event_processor(self):
        """Process incoming events from external sources"""
        while self.running:
            try:
                # TODO: Implement event ingestion from ZeroMQ, test bus, etc.
                await asyncio.sleep(1)
            except Exception as e:
                self.logger.error("Error in event processor: %s", e, exc_info=True)
                await asyncio.sleep(5)
    
    async def _health_monitor(self):
        """Monitor LUPIS health and performance"""
        while self.running:
            try:
                # Check memory usage, CPU, etc.
                # TODO: Implement actual health monitoring
                await asyncio.sleep(self.config.monitoring.health_check_interval)
            except Exception as e:
                self.logger.error("Error in health monitor: %s", e, exc_info=True)
                await asyncio.sleep(10)
    
    async def _periodic_tasks(self):
        """Run periodic maintenance tasks"""
        while self.running:
            try:
                # Daily token grant
                now = datetime.now()
                if now.hour == 0 and now.minute == 0:  # Midnight
                    if self.ucoin_ledger:
                        granted = self.ucoin_ledger.daily_grant()
                        if granted > 0:
                            self.logger.info("Granted daily U-Coin allowance: %d tokens", granted)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error("Error in periodic tasks: %s", e, exc_info=True)
                await asyncio.sleep(60)
    
    # Public API methods for external integration
    
    async def submit_metric_event(self, metric: str, value: float, source: str, metadata: Dict[str, Any] = None):
        """Submit a metric event to LUPIS"""
        event = MetricEvent(
            metric=metric,
            value=value,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata or {}
        )
        await self.metric_queue.put(event)
    
    async def submit_drift_report(self, component: str, score: float, evidence: Dict[str, Any]):
        """Submit a drift report to LUPIS"""
        report = DriftReport(
            component=component,
            score=score,
            evidence=evidence,
            timestamp=datetime.now(),
            severity="warning" if score > 0.5 else "info"
        )
        await self.drift_queue.put(report)
    
    async def submit_user_feedback(self, session_id: str, sentiment: str, note: str, metadata: Dict[str, Any] = None):
        """Submit user feedback to LUPIS"""
        feedback = UserFeedback(
            session_id=session_id,
            sentiment=sentiment,
            note=note,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        await self.feedback_queue.put(feedback)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LUPIS performance statistics"""
        return {
            'processed_events': self.processed_events,
            'optimization_tickets_created': self.optimization_tickets_created,
            'consecutive_failures': self.consecutive_failures,
            'running': self.running,
            'uptime_seconds': (datetime.now() - self.last_kpi_check).total_seconds(),
            'config_version': self.config.version
        }


# Factory function for easy instantiation
def create_lupis_orchestrator(environment: str = None) -> LUPISOrchestrator:
    """Create LUPIS orchestrator with appropriate configuration"""
    config = get_lupis_config(environment)
    return LUPISOrchestrator(config)


if __name__ == "__main__":
    # Example usage
    async def main():
        lupis = create_lupis_orchestrator()
        try:
            await lupis.start()
        except KeyboardInterrupt:
            await lupis.stop()
    
    asyncio.run(main())