#!/usr/bin/env python3
"""
User-Story Synthesiser Configuration
Central configuration for USS system parameters and integration settings
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    db_path: str = str(Path.home() / "qtm3" / "core.db")
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backups: int = 7
    connection_timeout: int = 30
    

@dataclass
class ComponentDiscoveryConfig:
    """Component discovery and classification settings"""
    # File patterns for component discovery
    component_patterns: Dict[str, List[str]] = field(default_factory=lambda: {
        'agent': [
            r'agents?.*\.py$',
            r'.*agent.*\.py$', 
            r'.*_agent\.py$'
        ],
        'service': [
            r'services?.*\.py$',
            r'.*service.*\.py$',
            r'.*_service\.py$'
        ],
        'model': [
            r'models?.*\.py$',
            r'.*model.*\.py$',
            r'.*_model\.py$'
        ],
        'handler': [
            r'handlers?.*\.py$',
            r'.*handler.*\.py$',
            r'.*_handler\.py$'
        ],
        'manager': [
            r'managers?.*\.py$',
            r'.*manager.*\.py$',
            r'.*_manager\.py$'
        ],
        'controller': [
            r'controllers?.*\.py$',
            r'.*controller.*\.py$',
            r'.*_controller\.py$'
        ],
        'utility': [
            r'utils?.*\.py$',
            r'utilities.*\.py$',
            r'.*util.*\.py$',
            r'helpers?.*\.py$'
        ],
        'config': [
            r'config.*\.py$',
            r'.*config.*\.py$',
            r'settings.*\.py$'
        ],
        'test': [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'tests?.*\.py$'
        ],
        'script': [
            r'scripts?.*\.py$',
            r'.*\.sh$',
            r'.*\.zsh$',
            r'.*\.bash$'
        ]
    })
    
    # Files and directories to exclude from discovery
    excluded_patterns: List[str] = field(default_factory=lambda: [
        r'__pycache__',
        r'\.pyc$',
        r'\.pyo$',
        r'\.git',
        r'\.DS_Store',
        r'\.env',
        r'venv/',
        r'node_modules/',
        r'\.pytest_cache',
        r'\.vscode',
        r'\.idea'
    ])
    
    # Minimum confidence score for component discovery
    min_discovery_confidence: float = 0.6
    
    # Maximum file size to analyze (in bytes)
    max_file_size: int = 1024 * 1024  # 1MB


@dataclass
class StoryGenerationConfig:
    """User story generation settings"""
    # Quality score thresholds
    min_quality_score: float = 0.6
    high_quality_threshold: float = 0.8
    
    # Template-based generation settings
    max_story_length_words: int = 25
    min_story_length_words: int = 8
    
    # Story format requirements
    required_story_format: Dict[str, str] = field(default_factory=lambda: {
        'persona': 'As a',
        'goal': 'I want',
        'benefit': 'so that'
    })
    
    # Value proposition keywords
    value_keywords: List[str] = field(default_factory=lambda: [
        'efficiency', 'automation', 'clarity', 'control', 'confidence',
        'reliability', 'speed', 'accuracy', 'convenience', 'insight'
    ])
    
    # Touch point categories
    touchpoint_categories: List[str] = field(default_factory=lambda: [
        'Command-line interface', 'API endpoints', 'User interface',
        'Configuration files', 'Database operations', 'File operations',
        'Network operations', 'Internal interfaces'
    ])


@dataclass
class AnalysisConfig:
    """Component analysis configuration"""
    # Analysis timeouts (in seconds)
    structure_analysis_timeout: int = 30
    behavior_analysis_timeout: int = 30
    interaction_analysis_timeout: int = 30
    
    # Analysis depth levels
    max_ast_depth: int = 10
    max_dependency_depth: int = 5
    
    # Pattern matching settings
    case_sensitive_patterns: bool = False
    include_docstring_analysis: bool = True
    include_comment_analysis: bool = False


@dataclass
class MonitoringConfig:
    """Amebic monitoring configuration"""
    # File watching settings
    watch_paths: List[str] = field(default_factory=lambda: ['.'])
    recursive_watching: bool = True
    
    # Change processing settings
    batch_size: int = 10
    scan_interval_seconds: float = 5.0
    debounce_delay_seconds: float = 2.0
    
    # File system event filters
    ignored_file_extensions: List[str] = field(default_factory=lambda: [
        '.pyc', '.pyo', '.log', '.tmp', '.swp', '.bak'
    ])
    
    # Monitoring limits
    max_pending_changes: int = 1000
    max_file_size_mb: int = 10


@dataclass
class DriftDetectionConfig:
    """Component drift detection settings"""
    # Drift thresholds
    structure_drift_threshold: float = 0.3
    behavior_drift_threshold: float = 0.4
    interaction_drift_threshold: float = 0.2
    
    # Drift calculation weights
    drift_weights: Dict[str, float] = field(default_factory=lambda: {
        'structure': 0.3,
        'behavior': 0.4,
        'interactions': 0.2,
        'relationships': 0.1
    })
    
    # Alert thresholds
    warning_drift_score: float = 0.5
    critical_drift_score: float = 0.7
    
    # Drift history settings
    max_drift_history: int = 100
    drift_check_interval_hours: int = 6


@dataclass
class IntegrationConfig:
    """Integration with existing QTM3 system"""
    # Agent communication settings
    socket_timeout: int = 30
    max_message_size: int = 1024 * 1024  # 1MB
    
    # Orchestrator integration
    orchestrator_enabled: bool = True
    auto_register_agents: bool = True
    
    # Existing agent integration
    perception_agent_integration: bool = True
    memory_agent_integration: bool = True
    reasoning_agent_integration: bool = False  # Future enhancement
    
    # Event publishing
    publish_component_events: bool = True
    publish_story_events: bool = True
    publish_drift_events: bool = True


@dataclass
class PerformanceConfig:
    """Performance optimization settings"""
    # Caching settings
    enable_analysis_cache: bool = True
    cache_ttl_hours: int = 24
    max_cache_size_mb: int = 100
    
    # Parallel processing
    max_worker_threads: int = 4
    enable_async_processing: bool = True
    
    # Memory management
    max_memory_usage_mb: int = 500
    garbage_collection_interval: int = 100


@dataclass
class LoggingConfig:
    """Logging configuration"""
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file_path: str = str(Path.home() / "qtm3" / "logs" / "uss.log")
    max_log_file_size_mb: int = 10
    max_log_files: int = 5
    
    # Component-specific logging
    component_log_levels: Dict[str, str] = field(default_factory=lambda: {
        'qtm3.component_registry': 'INFO',
        'qtm3.user_story_synthesiser': 'INFO',
        'qtm3.amebic_monitor': 'DEBUG',
        'qtm3.component_analyzer': 'INFO',
        'qtm3.story_generator': 'INFO'
    })


@dataclass
class USSConfig:
    """Main USS system configuration"""
    # Core configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    discovery: ComponentDiscoveryConfig = field(default_factory=ComponentDiscoveryConfig)
    story_generation: StoryGenerationConfig = field(default_factory=StoryGenerationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    drift_detection: DriftDetectionConfig = field(default_factory=DriftDetectionConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # System metadata
    version: str = "1.0.0"
    environment: str = "development"
    debug_mode: bool = True
    
    @classmethod
    def from_environment(cls) -> 'USSConfig':
        """Create configuration from environment variables"""
        config = cls()
        
        # Override with environment variables
        if os.getenv('USS_DB_PATH'):
            config.database.db_path = os.getenv('USS_DB_PATH')
        
        if os.getenv('USS_LOG_LEVEL'):
            config.logging.log_level = os.getenv('USS_LOG_LEVEL')
        
        if os.getenv('USS_DEBUG_MODE'):
            config.debug_mode = os.getenv('USS_DEBUG_MODE').lower() == 'true'
        
        if os.getenv('USS_ENVIRONMENT'):
            config.environment = os.getenv('USS_ENVIRONMENT')
        
        # Watch paths from environment
        if os.getenv('USS_WATCH_PATHS'):
            paths = os.getenv('USS_WATCH_PATHS').split(':')
            config.monitoring.watch_paths = paths
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'database': self.database.__dict__,
            'discovery': self.discovery.__dict__,
            'story_generation': self.story_generation.__dict__,
            'analysis': self.analysis.__dict__,
            'monitoring': self.monitoring.__dict__,
            'drift_detection': self.drift_detection.__dict__,
            'integration': self.integration.__dict__,
            'performance': self.performance.__dict__,
            'logging': self.logging.__dict__,
            'version': self.version,
            'environment': self.environment,
            'debug_mode': self.debug_mode
        }
    
    def validate(self) -> List[str]:
        """Validate configuration settings"""
        errors = []
        
        # Validate database path
        db_path = Path(self.database.db_path)
        if not db_path.parent.exists():
            errors.append(f"Database directory does not exist: {db_path.parent}")
        
        # Validate watch paths
        for watch_path in self.monitoring.watch_paths:
            if not Path(watch_path).exists():
                errors.append(f"Watch path does not exist: {watch_path}")
        
        # Validate thresholds
        if not 0.0 <= self.story_generation.min_quality_score <= 1.0:
            errors.append("Quality score threshold must be between 0.0 and 1.0")
        
        if not 0.0 <= self.discovery.min_discovery_confidence <= 1.0:
            errors.append("Discovery confidence threshold must be between 0.0 and 1.0")
        
        # Validate performance settings
        if self.performance.max_worker_threads <= 0:
            errors.append("Max worker threads must be positive")
        
        if self.performance.max_memory_usage_mb <= 0:
            errors.append("Max memory usage must be positive")
        
        return errors


# Global configuration instance
DEFAULT_CONFIG = USSConfig()

# Environment-specific configurations
DEVELOPMENT_CONFIG = USSConfig()
DEVELOPMENT_CONFIG.debug_mode = True
DEVELOPMENT_CONFIG.logging.log_level = "DEBUG"
DEVELOPMENT_CONFIG.performance.enable_analysis_cache = False

PRODUCTION_CONFIG = USSConfig()
PRODUCTION_CONFIG.debug_mode = False
PRODUCTION_CONFIG.environment = "production"
PRODUCTION_CONFIG.logging.log_level = "INFO"
PRODUCTION_CONFIG.performance.max_worker_threads = 8
PRODUCTION_CONFIG.performance.max_memory_usage_mb = 1000


def get_config(environment: str = None) -> USSConfig:
    """Get configuration for specified environment"""
    env = environment or os.getenv('USS_ENVIRONMENT', 'development')
    
    if env == 'production':
        return PRODUCTION_CONFIG
    elif env == 'development':
        return DEVELOPMENT_CONFIG
    else:
        return USSConfig.from_environment()


def load_config_from_file(config_path: Path) -> USSConfig:
    """Load configuration from JSON file"""
    import json
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # Basic implementation - would need more sophisticated deserialization
    # for production use
    config = USSConfig()
    
    # Override defaults with loaded values
    for section, values in config_data.items():
        if hasattr(config, section):
            section_obj = getattr(config, section)
            for key, value in values.items():
                if hasattr(section_obj, key):
                    setattr(section_obj, key, value)
    
    return config


def save_config_to_file(config: USSConfig, config_path: Path):
    """Save configuration to JSON file"""
    import json
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config.to_dict(), f, indent=2)