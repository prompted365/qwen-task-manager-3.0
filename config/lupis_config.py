#!/usr/bin/env python3
"""
LUPIS (Loop-Updating Perception-Intelligence Synthesiser) Configuration
Central configuration for LUPIS system parameters and integration settings
Version: 2025-06-17
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class AutomationGate(Enum):
    """Automation gates for different actions"""
    ALWAYS = "always"
    ROI_GATE = "roi_gate"  # ROI >= 0.6 and Urgency >= 0.5
    HIGH_ROI = "high_roi"  # ROI >= 0.8
    MANUAL_ONLY = "manual_only"


@dataclass
class UCoinConfig:
    """U-Coin economy configuration"""
    # Token costs
    create_ticket_cost: int = 5
    spawn_agent_cost: int = 20
    prompt_mutation_cost: int = 2
    failed_action_penalty: int = 10
    
    # Token rewards
    successful_ticket_reward: int = 10  # multiplied by ROI
    successful_agent_reward: int = 50
    successful_mutation_reward: int = 5
    
    # Balance management
    initial_balance: int = 100
    max_balance: int = 1000
    min_balance_for_auto: int = 10
    
    # Token refresh
    daily_token_grant: int = 20
    quality_bonus_multiplier: float = 1.5


@dataclass
class SensorConfig:
    """Sensor configuration for telemetry and feedback collection"""
    # ZeroMQ telemetry
    telemetry_port: int = 5555
    telemetry_timeout: int = 5000
    
    # Test bus integration
    pytest_plugin_enabled: bool = True
    test_failure_threshold: int = 3
    
    # Feedback ingestion
    feedback_port: int = 5556
    feedback_rate_limit: int = 100  # messages per minute
    
    # Polling intervals
    kpi_poll_interval: int = 300  # 5 minutes
    drift_check_interval: int = 21600  # 6 hours
    batch_processing_interval: int = 86400  # daily


@dataclass
class AnalyzerConfig:
    """Analyzer configuration for drift detection and ROI estimation"""
    # Drift detection
    structure_weight: float = 0.3
    behavior_weight: float = 0.4
    interaction_weight: float = 0.2
    relationship_weight: float = 0.1
    
    # ROI calculation
    effort_estimation_model: str = "story_points"
    max_effort_threshold: int = 8  # story points
    business_value_multiplier: float = 10.0
    
    # Thresholds
    drift_threshold: float = 0.5
    roi_threshold: float = 0.6
    urgency_threshold: float = 0.5
    
    # Analysis timeouts
    drift_analysis_timeout: int = 30
    roi_calculation_timeout: int = 15


@dataclass
class ActuatorConfig:
    """Actuator configuration for automated actions"""
    # GitHub integration
    github_api_token: Optional[str] = None
    github_repo: Optional[str] = None
    github_project: Optional[str] = "qwen-task-manager-3.0"
    
    # Automation gates
    ticket_automation_gate: AutomationGate = AutomationGate.ROI_GATE
    agent_spawn_gate: AutomationGate = AutomationGate.HIGH_ROI
    prompt_mutation_gate: AutomationGate = AutomationGate.ROI_GATE
    
    # Rate limiting
    max_tickets_per_hour: int = 10
    max_agents_per_day: int = 2
    max_mutations_per_hour: int = 5
    
    # PR/Issue templates
    ticket_prefix: str = "[LUPIS]"
    auto_merge_feature_flags: bool = True


@dataclass
class AuditConfig:
    """Audit and traceability configuration"""
    # Audit storage
    audit_path: str = str(Path.home() / "qtm3" / "audit")
    audit_file: str = "lupis_audit.yaml"
    
    # Immutable chain
    chain_enabled: bool = True
    chain_file: str = "audit-chain.sqlite"
    
    # Signing and verification
    sign_entries: bool = True
    hash_algorithm: str = "sha256"
    
    # Retention
    max_audit_entries: int = 10000
    audit_retention_days: int = 365
    
    # Backup
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    offsite_backup_enabled: bool = False
    s3_bucket: Optional[str] = None


@dataclass
class MutationConfig:
    """Mutation engine configuration"""
    # Generation settings
    max_options_per_mutation: int = 5
    option_generation_timeout: int = 60
    
    # Scoring weights
    roi_weight: float = 0.4
    risk_weight: float = 0.3
    effort_weight: float = 0.2
    compatibility_weight: float = 0.1
    
    # Mutation types
    enabled_mutations: List[str] = field(default_factory=lambda: [
        "prompt_tuning",
        "test_generation", 
        "micro_agent_creation",
        "config_optimization"
    ])
    
    # Safety settings
    auto_revert_on_failure: bool = True
    monitoring_window_hours: int = 24
    max_concurrent_mutations: int = 3


@dataclass
class IntegrationConfig:
    """Integration with QTM3 and external systems"""
    # QTM3 components
    qtm3_socket_path: str = "/tmp/qtm.sock"
    uss_integration: bool = True
    component_registry_integration: bool = True
    
    # Agent communication
    architect_endpoint: Optional[str] = None
    orchestrator_endpoint: Optional[str] = None
    
    # External APIs
    github_enabled: bool = True
    slack_enabled: bool = False
    discord_enabled: bool = False
    
    # Event publishing
    publish_to_qtm3_bus: bool = True
    event_batch_size: int = 10


@dataclass
class MonitoringConfig:
    """LUPIS self-monitoring configuration"""
    # KPI targets
    ticket_acceptance_rate_target: float = 0.7
    kpi_regression_threshold: float = 0.05
    drift_false_negative_threshold: float = 0.03
    max_explanation_length: int = 180
    
    # Health checks
    health_check_interval: int = 60
    memory_usage_threshold_mb: int = 500
    cpu_usage_threshold_percent: float = 80.0
    
    # Alerting
    alert_on_consecutive_failures: int = 3
    escalation_timeout_minutes: int = 30


@dataclass
class SecurityConfig:
    """Security and sandboxing configuration"""
    # Sandboxing
    enable_seccomp: bool = True
    restrict_network_access: bool = True
    allowed_domains: List[str] = field(default_factory=lambda: [
        "api.github.com",
        "github.com"
    ])
    
    # Container settings
    container_memory_limit: str = "200MB"
    container_cpu_limit: str = "0.5"
    
    # File system access
    readonly_paths: List[str] = field(default_factory=lambda: [
        "/etc",
        "/usr",
        "/lib"
    ])
    
    writable_paths: List[str] = field(default_factory=lambda: [
        "/tmp",
        str(Path.home() / "qtm3")
    ])


@dataclass
class LUPISConfig:
    """Main LUPIS system configuration"""
    # Core configurations
    ucoin: UCoinConfig = field(default_factory=UCoinConfig)
    sensors: SensorConfig = field(default_factory=SensorConfig)
    analyzers: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    actuators: ActuatorConfig = field(default_factory=ActuatorConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    mutation: MutationConfig = field(default_factory=MutationConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # System metadata
    version: str = "2025-06-17"
    environment: str = "development"
    debug_mode: bool = True
    
    # Operational modes
    autonomous_mode: bool = False
    proposal_only_mode: bool = False
    
    @classmethod
    def from_environment(cls) -> 'LUPISConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Core settings
        if os.getenv('LUPIS_ENVIRONMENT'):
            config.environment = os.getenv('LUPIS_ENVIRONMENT')
        
        if os.getenv('LUPIS_DEBUG_MODE'):
            config.debug_mode = os.getenv('LUPIS_DEBUG_MODE').lower() == 'true'
        
        if os.getenv('LUPIS_AUTONOMOUS_MODE'):
            config.autonomous_mode = os.getenv('LUPIS_AUTONOMOUS_MODE').lower() == 'true'
        
        # GitHub integration
        if os.getenv('GITHUB_TOKEN'):
            config.actuators.github_api_token = os.getenv('GITHUB_TOKEN')
        
        if os.getenv('GITHUB_REPO'):
            config.actuators.github_repo = os.getenv('GITHUB_REPO')
        
        # U-Coin settings
        if os.getenv('LUPIS_INITIAL_BALANCE'):
            config.ucoin.initial_balance = int(os.getenv('LUPIS_INITIAL_BALANCE'))
        
        # Audit settings
        if os.getenv('LUPIS_AUDIT_PATH'):
            config.audit.audit_path = os.getenv('LUPIS_AUDIT_PATH')
        
        if os.getenv('S3_BACKUP_BUCKET'):
            config.audit.s3_bucket = os.getenv('S3_BACKUP_BUCKET')
            config.audit.offsite_backup_enabled = True
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'ucoin': self.ucoin.__dict__,
            'sensors': self.sensors.__dict__,
            'analyzers': self.analyzers.__dict__,
            'actuators': self.actuators.__dict__,
            'audit': self.audit.__dict__,
            'mutation': self.mutation.__dict__,
            'integration': self.integration.__dict__,
            'monitoring': self.monitoring.__dict__,
            'security': self.security.__dict__,
            'version': self.version,
            'environment': self.environment,
            'debug_mode': self.debug_mode,
            'autonomous_mode': self.autonomous_mode,
            'proposal_only_mode': self.proposal_only_mode
        }
    
    def validate(self) -> List[str]:
        """Validate configuration settings"""
        errors = []
        
        # Validate paths
        audit_path = Path(self.audit.audit_path)
        if not audit_path.parent.exists():
            errors.append(f"Audit directory parent does not exist: {audit_path.parent}")
        
        # Validate thresholds
        if not 0.0 <= self.analyzers.roi_threshold <= 1.0:
            errors.append("ROI threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= self.analyzers.urgency_threshold <= 1.0:
            errors.append("Urgency threshold must be between 0.0 and 1.0")
        
        # Validate U-Coin settings
        if self.ucoin.initial_balance < 0:
            errors.append("Initial U-Coin balance must be non-negative")
        
        if self.ucoin.min_balance_for_auto > self.ucoin.initial_balance:
            errors.append("Minimum balance for automation exceeds initial balance")
        
        # Validate rate limits
        if self.actuators.max_tickets_per_hour <= 0:
            errors.append("Max tickets per hour must be positive")
        
        # Validate GitHub settings if enabled
        if self.integration.github_enabled and not self.actuators.github_api_token:
            errors.append("GitHub token required when GitHub integration is enabled")
        
        return errors


# Environment-specific configurations
DEVELOPMENT_CONFIG = LUPISConfig()
DEVELOPMENT_CONFIG.debug_mode = True
DEVELOPMENT_CONFIG.autonomous_mode = False
DEVELOPMENT_CONFIG.ucoin.initial_balance = 50
DEVELOPMENT_CONFIG.actuators.max_tickets_per_hour = 5

PRODUCTION_CONFIG = LUPISConfig()
PRODUCTION_CONFIG.debug_mode = False
PRODUCTION_CONFIG.environment = "production"
PRODUCTION_CONFIG.autonomous_mode = True
PRODUCTION_CONFIG.ucoin.initial_balance = 200
PRODUCTION_CONFIG.audit.offsite_backup_enabled = True
PRODUCTION_CONFIG.security.enable_seccomp = True
PRODUCTION_CONFIG.security.restrict_network_access = True


def get_lupis_config(environment: str = None) -> LUPISConfig:
    """Get LUPIS configuration for specified environment"""
    env = environment or os.getenv('LUPIS_ENVIRONMENT', 'development')
    
    if env == 'production':
        return PRODUCTION_CONFIG
    elif env == 'development':
        return DEVELOPMENT_CONFIG
    else:
        return LUPISConfig.from_environment()


# Global configuration instance
DEFAULT_LUPIS_CONFIG = LUPISConfig()