-- User-Story Synthesiser Database Schema Extension
-- Extends the existing QTM3 database with USS-specific tables

PRAGMA journal_mode=WAL;

-- Component Registry Tables

-- Components table: tracks all first-class components in the system
CREATE TABLE IF NOT EXISTS components (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('agent', 'module', 'service', 'utility')),
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_analyzed TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'deprecated', 'flagged', 'archived'))
);

-- User stories table: stores USS-generated user stories for components
CREATE TABLE IF NOT EXISTS user_stories (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL,
    user_story TEXT NOT NULL,
    engagement TEXT NOT NULL CHECK(engagement IN ('direct', 'proxy')),
    primitive_value TEXT NOT NULL,
    expression TEXT NOT NULL,
    confidence_score REAL DEFAULT 0.0 CHECK(confidence_score >= 0.0 AND confidence_score <= 1.0),
    quality_score REAL DEFAULT 0.0 CHECK(quality_score >= 0.0 AND quality_score <= 1.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES components (id) ON DELETE CASCADE
);

-- Touch points table: stores I/O surfaces for user interactions
CREATE TABLE IF NOT EXISTS touch_points (
    id TEXT PRIMARY KEY,
    user_story_id TEXT NOT NULL,
    touch_point TEXT NOT NULL,
    touch_type TEXT CHECK(touch_type IN ('input', 'output', 'interface', 'event')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_story_id) REFERENCES user_stories (id) ON DELETE CASCADE
);

-- Drift metrics table: tracks component alignment drift over time
CREATE TABLE IF NOT EXISTS drift_metrics (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL,
    drift_score REAL NOT NULL CHECK(drift_score >= 0.0 AND drift_score <= 1.0),
    drift_type TEXT NOT NULL CHECK(drift_type IN ('implementation', 'interface', 'purpose', 'composite')),
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details TEXT, -- JSON details
    FOREIGN KEY (component_id) REFERENCES components (id) ON DELETE CASCADE
);

-- Component flags table: tracks components requiring attention
CREATE TABLE IF NOT EXISTS component_flags (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL,
    flag_level TEXT NOT NULL CHECK(flag_level IN ('none', 'minor', 'significant', 'critical')),
    drift_score REAL NOT NULL,
    details TEXT, -- JSON details
    flagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by TEXT,
    FOREIGN KEY (component_id) REFERENCES components (id) ON DELETE CASCADE
);

-- USS analysis log: tracks all USS operations for debugging
CREATE TABLE IF NOT EXISTS uss_analysis_log (
    id TEXT PRIMARY KEY,
    component_id TEXT NOT NULL,
    analysis_type TEXT NOT NULL CHECK(analysis_type IN ('initial', 'update', 'drift_check', 'scheduled')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running' CHECK(status IN ('running', 'completed', 'failed')),
    result_data TEXT, -- JSON result
    error_message TEXT,
    FOREIGN KEY (component_id) REFERENCES components (id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_components_type ON components(type);
CREATE INDEX IF NOT EXISTS idx_components_status ON components(status);
CREATE INDEX IF NOT EXISTS idx_components_file_path ON components(file_path);
CREATE INDEX IF NOT EXISTS idx_user_stories_component ON user_stories(component_id);
CREATE INDEX IF NOT EXISTS idx_user_stories_engagement ON user_stories(engagement);
CREATE INDEX IF NOT EXISTS idx_touch_points_story ON touch_points(user_story_id);
CREATE INDEX IF NOT EXISTS idx_drift_metrics_component ON drift_metrics(component_id);
CREATE INDEX IF NOT EXISTS idx_drift_metrics_score ON drift_metrics(drift_score);
CREATE INDEX IF NOT EXISTS idx_drift_metrics_type ON drift_metrics(drift_type);
CREATE INDEX IF NOT EXISTS idx_flags_component ON component_flags(component_id);
CREATE INDEX IF NOT EXISTS idx_flags_level ON component_flags(flag_level);
CREATE INDEX IF NOT EXISTS idx_flags_unresolved ON component_flags(resolved_at) WHERE resolved_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_analysis_log_component ON uss_analysis_log(component_id);
CREATE INDEX IF NOT EXISTS idx_analysis_log_status ON uss_analysis_log(status);

-- Views for common queries

-- Active components with their latest user stories
CREATE VIEW IF NOT EXISTS active_components_with_stories AS
SELECT 
    c.id as component_id,
    c.name,
    c.type,
    c.file_path,
    c.last_analyzed,
    us.user_story,
    us.engagement,
    us.primitive_value,
    us.quality_score,
    us.created_at as story_created
FROM components c
LEFT JOIN user_stories us ON c.id = us.component_id
WHERE c.status = 'active'
AND (us.id IS NULL OR us.id = (
    SELECT id FROM user_stories 
    WHERE component_id = c.id 
    ORDER BY created_at DESC 
    LIMIT 1
));

-- Components requiring attention (high drift or flagged)
CREATE VIEW IF NOT EXISTS components_requiring_attention AS
SELECT 
    c.id as component_id,
    c.name,
    c.type,
    cf.flag_level,
    cf.flagged_at,
    dm.drift_score,
    dm.drift_type,
    dm.measured_at as drift_measured
FROM components c
LEFT JOIN component_flags cf ON c.id = cf.component_id AND cf.resolved_at IS NULL
LEFT JOIN drift_metrics dm ON c.id = dm.component_id
WHERE (cf.flag_level IN ('significant', 'critical') OR dm.drift_score > 0.6)
AND c.status = 'active'
ORDER BY 
    CASE cf.flag_level 
        WHEN 'critical' THEN 4
        WHEN 'significant' THEN 3
        WHEN 'minor' THEN 2
        ELSE 1
    END DESC,
    dm.drift_score DESC;

-- USS coverage statistics
CREATE VIEW IF NOT EXISTS uss_coverage_stats AS
SELECT 
    c.type as component_type,
    COUNT(*) as total_components,
    COUNT(us.id) as analyzed_components,
    ROUND(CAST(COUNT(us.id) AS FLOAT) / COUNT(*) * 100, 2) as coverage_percentage,
    AVG(us.quality_score) as avg_quality_score
FROM components c
LEFT JOIN user_stories us ON c.id = us.component_id
WHERE c.status = 'active'
GROUP BY c.type;