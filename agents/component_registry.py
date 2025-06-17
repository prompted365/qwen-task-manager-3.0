#!/usr/bin/env python3
"""
Component Registry Manager
Handles CRUD operations for USS component and user story data
"""

import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging


class ComponentRegistry:
    """Central registry for component-user story mappings"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.logger = logging.getLogger("qtm3.component_registry")
        self._init_registry_schema()
    
    def _init_registry_schema(self):
        """Initialize component registry tables if they don't exist"""
        schema_path = Path(__file__).parent.parent / "database" / "uss_schema.sql"
        
        if schema_path.exists():
            with sqlite3.connect(self.db_path) as conn:
                schema_sql = schema_path.read_text()
                conn.executescript(schema_sql)
                self.logger.info("USS schema initialized")
        else:
            self.logger.warning(f"USS schema file not found at {schema_path}")
    
    def register_component(self, component_info: Dict[str, Any]) -> str:
        """Register a new component for USS analysis"""
        component_id = f"comp_{uuid.uuid4().hex[:8]}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO components (id, name, type, file_path)
                    VALUES (?, ?, ?, ?)
                """, (
                    component_id, 
                    component_info['name'], 
                    component_info.get('type', 'module'),
                    component_info.get('file_path')
                ))
                
                self.logger.info(f"Registered component: {component_info['name']} ({component_id})")
                return component_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to register component: {e}")
            raise
    
    def store_user_story(self, component_id: str, uss_output: Dict[str, Any]) -> str:
        """Store USS analysis results for a component"""
        story_id = f"story_{uuid.uuid4().hex[:8]}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store main user story
                conn.execute("""
                    INSERT INTO user_stories 
                    (id, component_id, user_story, engagement, primitive_value, 
                     expression, confidence_score, quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    story_id, 
                    component_id, 
                    uss_output['user_story'],
                    uss_output['engagement'], 
                    uss_output['primitive_value'],
                    uss_output['expression'],
                    uss_output.get('confidence', 0.0),
                    uss_output.get('quality_score', 0.0)
                ))
                
                # Store touch points
                for touch_point in uss_output.get('touch_points', []):
                    touch_id = f"tp_{uuid.uuid4().hex[:8]}"
                    conn.execute("""
                        INSERT INTO touch_points (id, user_story_id, touch_point, touch_type)
                        VALUES (?, ?, ?, ?)
                    """, (touch_id, story_id, touch_point, 'interface'))
                
                # Update component's last_analyzed timestamp
                conn.execute("""
                    UPDATE components 
                    SET last_analyzed = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (component_id,))
                
                self.logger.info(f"Stored user story for component {component_id}: {story_id}")
                return story_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store user story: {e}")
            raise
    
    def get_component_story(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve current user story for component"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get latest user story
                story_result = conn.execute("""
                    SELECT * FROM user_stories 
                    WHERE component_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (component_id,)).fetchone()
                
                if not story_result:
                    return None
                
                # Get touch points
                touch_points = conn.execute("""
                    SELECT touch_point FROM touch_points 
                    WHERE user_story_id = ?
                """, (story_result['id'],)).fetchall()
                
                return {
                    'id': story_result['id'],
                    'user_story': story_result['user_story'],
                    'engagement': story_result['engagement'],
                    'primitive_value': story_result['primitive_value'],
                    'expression': story_result['expression'],
                    'confidence_score': story_result['confidence_score'],
                    'quality_score': story_result['quality_score'],
                    'touch_points': [tp['touch_point'] for tp in touch_points],
                    'created_at': story_result['created_at']
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get component story: {e}")
            return None
    
    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve component information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                result = conn.execute("""
                    SELECT * FROM components WHERE id = ?
                """, (component_id,)).fetchone()
                
                return dict(result) if result else None
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get component: {e}")
            return None
    
    def list_components(self, status: str = 'active', component_type: str = None) -> List[Dict[str, Any]]:
        """List components with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = "SELECT * FROM components WHERE status = ?"
                params = [status]
                
                if component_type:
                    query += " AND type = ?"
                    params.append(component_type)
                
                query += " ORDER BY created_at DESC"
                
                results = conn.execute(query, params).fetchall()
                return [dict(row) for row in results]
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to list components: {e}")
            return []
    
    def update_component_status(self, component_id: str, status: str) -> bool:
        """Update component status"""
        valid_statuses = ['active', 'deprecated', 'flagged', 'archived']
        if status not in valid_statuses:
            self.logger.error(f"Invalid status: {status}")
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE components SET status = ? WHERE id = ?
                """, (status, component_id))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Updated component {component_id} status to {status}")
                    return True
                else:
                    self.logger.warning(f"Component {component_id} not found")
                    return False
                    
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update component status: {e}")
            return False
    
    def store_drift_metric(self, component_id: str, drift_score: float, 
                          drift_type: str, details: Dict[str, Any] = None) -> str:
        """Store drift metric for component"""
        metric_id = f"drift_{uuid.uuid4().hex[:8]}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO drift_metrics 
                    (id, component_id, drift_score, drift_type, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    metric_id, 
                    component_id, 
                    drift_score, 
                    drift_type,
                    json.dumps(details) if details else None
                ))
                
                self.logger.info(f"Stored drift metric for {component_id}: {drift_score}")
                return metric_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store drift metric: {e}")
            raise
    
    def get_drift_metrics(self, component_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent drift metrics for component"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                results = conn.execute("""
                    SELECT * FROM drift_metrics 
                    WHERE component_id = ? 
                    ORDER BY measured_at DESC 
                    LIMIT ?
                """, (component_id, limit)).fetchall()
                
                metrics = []
                for row in results:
                    metric = dict(row)
                    if metric['details']:
                        metric['details'] = json.loads(metric['details'])
                    metrics.append(metric)
                
                return metrics
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get drift metrics: {e}")
            return []
    
    def store_component_flag(self, component_id: str, flag_level: str, 
                           drift_score: float, details: Dict[str, Any] = None) -> str:
        """Store component flag for attention"""
        flag_id = f"flag_{uuid.uuid4().hex[:8]}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO component_flags 
                    (id, component_id, flag_level, drift_score, details)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    flag_id, 
                    component_id, 
                    flag_level, 
                    drift_score,
                    json.dumps(details) if details else None
                ))
                
                self.logger.info(f"Flagged component {component_id} as {flag_level}")
                return flag_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to store component flag: {e}")
            raise
    
    def get_flagged_components(self, flag_level: str = None) -> List[Dict[str, Any]]:
        """Get components requiring attention"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                query = """
                    SELECT c.*, cf.flag_level, cf.drift_score, cf.flagged_at, cf.details
                    FROM components c
                    JOIN component_flags cf ON c.id = cf.component_id
                    WHERE cf.resolved_at IS NULL
                """
                params = []
                
                if flag_level:
                    query += " AND cf.flag_level = ?"
                    params.append(flag_level)
                
                query += " ORDER BY cf.flagged_at DESC"
                
                results = conn.execute(query, params).fetchall()
                
                flagged = []
                for row in results:
                    item = dict(row)
                    if item['details']:
                        item['details'] = json.loads(item['details'])
                    flagged.append(item)
                
                return flagged
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get flagged components: {e}")
            return []
    
    def resolve_flag(self, component_id: str, resolved_by: str = None) -> bool:
        """Mark component flag as resolved"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE component_flags 
                    SET resolved_at = CURRENT_TIMESTAMP, resolved_by = ?
                    WHERE component_id = ? AND resolved_at IS NULL
                """, (resolved_by, component_id))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Resolved flag for component {component_id}")
                    return True
                else:
                    self.logger.warning(f"No unresolved flags found for component {component_id}")
                    return False
                    
        except sqlite3.Error as e:
            self.logger.error(f"Failed to resolve flag: {e}")
            return False
    
    def get_coverage_stats(self) -> Dict[str, Any]:
        """Get USS coverage statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                results = conn.execute("""
                    SELECT * FROM uss_coverage_stats
                """).fetchall()
                
                stats = {}
                total_components = 0
                total_analyzed = 0
                
                for row in results:
                    row_dict = dict(row)
                    stats[row_dict['component_type']] = {
                        'total': row_dict['total_components'],
                        'analyzed': row_dict['analyzed_components'],
                        'coverage': row_dict['coverage_percentage'],
                        'avg_quality': row_dict['avg_quality_score']
                    }
                    total_components += row_dict['total_components']
                    total_analyzed += row_dict['analyzed_components']
                
                overall_coverage = (total_analyzed / total_components * 100) if total_components > 0 else 0
                
                return {
                    'by_type': stats,
                    'overall': {
                        'total_components': total_components,
                        'analyzed_components': total_analyzed,
                        'coverage_percentage': round(overall_coverage, 2)
                    }
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get coverage stats: {e}")
            return {}
    
    def log_analysis(self, component_id: str, analysis_type: str, 
                    status: str = 'running', result_data: Dict = None, 
                    error_message: str = None) -> str:
        """Log USS analysis operation"""
        log_id = f"log_{uuid.uuid4().hex[:8]}"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                if status == 'completed':
                    conn.execute("""
                        INSERT INTO uss_analysis_log 
                        (id, component_id, analysis_type, status, result_data, completed_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        log_id, component_id, analysis_type, status,
                        json.dumps(result_data) if result_data else None
                    ))
                elif status == 'failed':
                    conn.execute("""
                        INSERT INTO uss_analysis_log 
                        (id, component_id, analysis_type, status, error_message, completed_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (log_id, component_id, analysis_type, status, error_message))
                else:
                    conn.execute("""
                        INSERT INTO uss_analysis_log 
                        (id, component_id, analysis_type, status)
                        VALUES (?, ?, ?, ?)
                    """, (log_id, component_id, analysis_type, status))
                
                return log_id
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to log analysis: {e}")
            raise