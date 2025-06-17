#!/usr/bin/env python3
"""
Amebic Monitor Agent
Continuous monitoring agent that watches for component changes and triggers USS analysis
"""

import os
import time
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Import base Agent class
import sys
sys.path.append(str(Path(__file__).parent.parent))
from agents import Agent
from agents.component_registry import ComponentRegistry
from agents.user_story_synthesiser import UserStorySynthesiserAgent


@dataclass
class ComponentChange:
    """Represents a detected component change"""
    file_path: Path
    change_type: str  # 'created', 'modified', 'deleted', 'moved'
    timestamp: datetime
    file_hash: Optional[str] = None
    old_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'file_path': str(self.file_path),
            'change_type': self.change_type,
            'timestamp': self.timestamp.isoformat(),
            'file_hash': self.file_hash,
            'old_path': str(self.old_path) if self.old_path else None
        }


@dataclass
class ComponentDiscovery:
    """Represents a discovered component"""
    name: str
    type: str
    file_path: Path
    confidence: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'name': self.name,
            'type': self.type,
            'file_path': str(self.file_path),
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class ComponentDiscoverer:
    """Discovers and classifies components from file changes"""
    
    def __init__(self):
        self.logger = logging.getLogger("qtm3.component_discoverer")
        
        # File patterns for component types
        self.component_patterns = {
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
        }
        
        # Excluded patterns (files to ignore)
        self.excluded_patterns = [
            r'__pycache__',
            r'\.pyc$',
            r'\.pyo$',
            r'\.git',
            r'\.DS_Store',
            r'\.env',
            r'venv/',
            r'node_modules/',
            r'\.pytest_cache'
        ]
    
    def discover_component(self, file_path: Path) -> Optional[ComponentDiscovery]:
        """Discover and classify a component from file path"""
        try:
            # Check if file should be excluded
            if self._should_exclude(file_path):
                return None
            
            # Determine component type
            component_type = self._classify_component(file_path)
            if not component_type:
                return None
            
            # Extract component name
            component_name = self._extract_component_name(file_path)
            
            # Calculate confidence score
            confidence = self._calculate_discovery_confidence(file_path, component_type)
            
            # Extract metadata
            metadata = self._extract_metadata(file_path)
            
            return ComponentDiscovery(
                name=component_name,
                type=component_type,
                file_path=file_path,
                confidence=confidence,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to discover component for {file_path}: {e}")
            return None
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from discovery"""
        import re
        
        path_str = str(file_path)
        for pattern in self.excluded_patterns:
            if re.search(pattern, path_str):
                return True
        return False
    
    def _classify_component(self, file_path: Path) -> Optional[str]:
        """Classify component type based on file path patterns"""
        import re
        
        path_str = str(file_path.name)
        
        # Check each component type pattern
        for component_type, patterns in self.component_patterns.items():
            for pattern in patterns:
                if re.search(pattern, path_str, re.IGNORECASE):
                    return component_type
        
        # Check for Python files that might be components
        if file_path.suffix == '.py':
            return 'module'
        
        return None
    
    def _extract_component_name(self, file_path: Path) -> str:
        """Extract meaningful component name from file path"""
        # Remove file extension
        name = file_path.stem
        
        # Clean up common prefixes/suffixes
        name = name.replace('_agent', '').replace('_service', '').replace('_manager', '')
        name = name.replace('_handler', '').replace('_controller', '').replace('_model', '')
        name = name.replace('test_', '').replace('_test', '')
        
        # Convert to readable format
        name = name.replace('_', ' ').title()
        
        return name or file_path.stem
    
    def _calculate_discovery_confidence(self, file_path: Path, component_type: str) -> float:
        """Calculate confidence score for component discovery"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for well-structured paths
        path_parts = file_path.parts
        if any(part in ['agents', 'services', 'models', 'handlers'] for part in path_parts):
            confidence += 0.2
        
        # Boost confidence for clear naming patterns
        name = file_path.stem.lower()
        if component_type in name:
            confidence += 0.2
        
        # Boost confidence for Python files in appropriate directories
        if file_path.suffix == '.py' and component_type != 'module':
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata about the file"""
        try:
            stat = file_path.stat()
            return {
                'file_size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_extension': file_path.suffix,
                'directory': str(file_path.parent),
                'relative_path': str(file_path.relative_to(Path.cwd())) if file_path.is_relative_to(Path.cwd()) else str(file_path)
            }
        except Exception as e:
            self.logger.error(f"Failed to extract metadata for {file_path}: {e}")
            return {}


class AmebicFileHandler(FileSystemEventHandler):
    """File system event handler for amebic monitoring"""
    
    def __init__(self, amebic_monitor):
        self.amebic_monitor = amebic_monitor
        self.logger = logging.getLogger("qtm3.amebic_file_handler")
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self.amebic_monitor.handle_file_change(
                Path(event.src_path), 'created'
            )
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            self.amebic_monitor.handle_file_change(
                Path(event.src_path), 'modified'
            )
    
    def on_deleted(self, event):
        """Handle file deletion events"""
        if not event.is_directory:
            self.amebic_monitor.handle_file_change(
                Path(event.src_path), 'deleted'
            )
    
    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            self.amebic_monitor.handle_file_change(
                Path(event.dest_path), 'moved', old_path=Path(event.src_path)
            )


class AmebicMonitorAgent(Agent):
    """Amebic monitoring agent for continuous component discovery"""
    
    def __init__(self, watch_paths: List[Path] = None, db_path: Path = None):
        super().__init__("amebic_monitor")
        
        # Initialize paths and components
        self.watch_paths = watch_paths or [Path.cwd()]
        self.db_path = db_path or Path.home() / "qtm3" / "core.db"
        
        # Initialize core components
        self.registry = ComponentRegistry(self.db_path)
        self.discoverer = ComponentDiscoverer()
        self.uss_agent = UserStorySynthesiserAgent(self.db_path)
        
        # File watching infrastructure
        self.observer = Observer()
        self.file_handler = AmebicFileHandler(self)
        self.monitoring = False
        
        # Change tracking
        self.pending_changes: List[ComponentChange] = []
        self.file_hashes: Dict[str, str] = {}
        self.last_scan_time = datetime.now()
        
        # Configuration
        self.scan_interval = 5.0  # Seconds between change processing
        self.batch_size = 10  # Max changes to process at once
        
        self.logger.info("Amebic Monitor Agent initialized")
    
    def start_monitoring(self) -> Dict[str, Any]:
        """Start monitoring file system changes"""
        try:
            if self.monitoring:
                return {"status": "already_monitoring", "watch_paths": [str(p) for p in self.watch_paths]}
            
            # Set up file system watchers
            for watch_path in self.watch_paths:
                if watch_path.exists():
                    self.observer.schedule(self.file_handler, str(watch_path), recursive=True)
                    self.logger.info(f"Watching path: {watch_path}")
                else:
                    self.logger.warning(f"Watch path does not exist: {watch_path}")
            
            # Start observer
            self.observer.start()
            self.monitoring = True
            
            # Perform initial discovery scan
            self._perform_initial_scan()
            
            self.logger.info("Amebic monitoring started")
            return {
                "status": "monitoring_started",
                "watch_paths": [str(p) for p in self.watch_paths],
                "initial_components": len(self.file_hashes)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return {"error": str(e)}
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring file system changes"""
        try:
            if not self.monitoring:
                return {"status": "not_monitoring"}
            
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.monitoring = False
            
            self.logger.info("Amebic monitoring stopped")
            return {"status": "monitoring_stopped"}
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return {"error": str(e)}
    
    def handle_file_change(self, file_path: Path, change_type: str, old_path: Path = None):
        """Handle individual file change events"""
        try:
            # Calculate file hash for change detection
            file_hash = None
            if change_type != 'deleted' and file_path.exists():
                file_hash = self._calculate_file_hash(file_path)
                
                # Skip if file hasn't actually changed
                if str(file_path) in self.file_hashes:
                    if self.file_hashes[str(file_path)] == file_hash:
                        return  # No actual change
            
            # Create change record
            change = ComponentChange(
                file_path=file_path,
                change_type=change_type,
                timestamp=datetime.now(),
                file_hash=file_hash,
                old_path=old_path
            )
            
            # Add to pending changes
            self.pending_changes.append(change)
            
            # Update file hash tracking
            if change_type == 'deleted':
                self.file_hashes.pop(str(file_path), None)
            elif file_hash:
                self.file_hashes[str(file_path)] = file_hash
            
            self.logger.debug(f"Detected {change_type}: {file_path}")
            
            # Process changes if batch is full or enough time has passed
            if (len(self.pending_changes) >= self.batch_size or 
                (datetime.now() - self.last_scan_time).total_seconds() >= self.scan_interval):
                self._process_pending_changes()
                
        except Exception as e:
            self.logger.error(f"Failed to handle file change {file_path}: {e}")
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle amebic monitor requests"""
        action = message.get("action")
        
        try:
            if action == "start_monitoring":
                return self.start_monitoring()
            elif action == "stop_monitoring":
                return self.stop_monitoring()
            elif action == "get_status":
                return self._get_monitoring_status()
            elif action == "force_scan":
                return self._force_full_scan()
            elif action == "get_recent_changes":
                return self._get_recent_changes(message.get("limit", 50))
            elif action == "add_watch_path":
                return self._add_watch_path(Path(message.get("path")))
            elif action == "remove_watch_path":
                return self._remove_watch_path(Path(message.get("path")))
            else:
                return {"error": f"Unknown action: {action}"}
        
        except Exception as e:
            self.logger.error(f"Error handling amebic monitor message: {e}")
            return {"error": str(e)}
    
    def _perform_initial_scan(self):
        """Perform initial discovery scan of all watch paths"""
        self.logger.info("Performing initial component discovery scan")
        
        discovered_count = 0
        for watch_path in self.watch_paths:
            if not watch_path.exists():
                continue
                
            for file_path in watch_path.rglob("*"):
                if file_path.is_file():
                    # Calculate and store file hash
                    file_hash = self._calculate_file_hash(file_path)
                    self.file_hashes[str(file_path)] = file_hash
                    
                    # Attempt component discovery
                    discovery = self.discoverer.discover_component(file_path)
                    if discovery and discovery.confidence > 0.6:
                        self._handle_component_discovery(discovery)
                        discovered_count += 1
        
        self.logger.info(f"Initial scan complete. Discovered {discovered_count} components")
    
    def _process_pending_changes(self):
        """Process all pending file changes"""
        if not self.pending_changes:
            return
        
        self.logger.debug(f"Processing {len(self.pending_changes)} pending changes")
        
        for change in self.pending_changes:
            try:
                # Attempt component discovery for relevant changes
                if change.change_type in ['created', 'modified', 'moved']:
                    discovery = self.discoverer.discover_component(change.file_path)
                    if discovery and discovery.confidence > 0.6:
                        self._handle_component_discovery(discovery, change)
                elif change.change_type == 'deleted':
                    self._handle_component_deletion(change)
                    
            except Exception as e:
                self.logger.error(f"Failed to process change {change.file_path}: {e}")
        
        # Clear processed changes
        self.pending_changes.clear()
        self.last_scan_time = datetime.now()
    
    def _handle_component_discovery(self, discovery: ComponentDiscovery, change: ComponentChange = None):
        """Handle discovery of a new or modified component"""
        try:
            # Prepare component info for registration
            component_info = {
                'name': discovery.name,
                'type': discovery.type,
                'file_path': str(discovery.file_path),
                'metadata': discovery.metadata,
                'discovery_confidence': discovery.confidence,
                'discovered_at': datetime.now().isoformat()
            }
            
            # Check if component is already registered
            existing_components = self.registry.get_components_by_path(str(discovery.file_path))
            
            if existing_components:
                # Component exists, check for changes
                component_id = existing_components[0]['id']
                if change and change.change_type == 'modified':
                    # Trigger re-analysis via USS agent
                    self.logger.info(f"Component modified, triggering re-analysis: {discovery.name}")
                    self._trigger_uss_analysis(component_info, component_id)
            else:
                # New component, register and analyze
                self.logger.info(f"New component discovered: {discovery.name}")
                component_id = self.registry.register_component(component_info)
                self._trigger_uss_analysis(component_info, component_id)
                
        except Exception as e:
            self.logger.error(f"Failed to handle component discovery: {e}")
    
    def _handle_component_deletion(self, change: ComponentChange):
        """Handle deletion of a component"""
        try:
            # Find and mark component as deleted
            existing_components = self.registry.get_components_by_path(str(change.file_path))
            for component in existing_components:
                component_id = component['id']
                self.registry.flag_component(component_id, 'deleted', f"File deleted: {change.file_path}")
                self.logger.info(f"Component marked as deleted: {component['name']}")
                
        except Exception as e:
            self.logger.error(f"Failed to handle component deletion: {e}")
    
    def _trigger_uss_analysis(self, component_info: Dict[str, Any], component_id: str = None):
        """Trigger USS analysis for component"""
        try:
            # Send analysis request to USS agent
            uss_message = {
                "action": "synthesize_story",
                "component_info": component_info
            }
            
            result = self.uss_agent.handle_message(uss_message)
            
            if "error" not in result:
                self.logger.info(f"USS analysis completed for {component_info['name']}")
            else:
                self.logger.error(f"USS analysis failed for {component_info['name']}: {result['error']}")
                
        except Exception as e:
            self.logger.error(f"Failed to trigger USS analysis: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring": self.monitoring,
            "watch_paths": [str(p) for p in self.watch_paths],
            "tracked_files": len(self.file_hashes),
            "pending_changes": len(self.pending_changes),
            "last_scan": self.last_scan_time.isoformat(),
            "observer_status": "running" if self.observer.is_alive() else "stopped"
        }
    
    def _force_full_scan(self) -> Dict[str, Any]:
        """Force a full rescan of all watch paths"""
        try:
            self.logger.info("Forcing full component rescan")
            
            # Clear current state
            old_count = len(self.file_hashes)
            self.file_hashes.clear()
            
            # Perform full scan
            self._perform_initial_scan()
            
            return {
                "scan_complete": True,
                "previous_files": old_count,
                "current_files": len(self.file_hashes),
                "scan_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to perform full scan: {e}")
            return {"error": str(e)}
    
    def _get_recent_changes(self, limit: int) -> Dict[str, Any]:
        """Get recent file changes"""
        try:
            recent_changes = [change.to_dict() for change in self.pending_changes[-limit:]]
            return {
                "changes": recent_changes,
                "total_pending": len(self.pending_changes)
            }
        except Exception as e:
            self.logger.error(f"Failed to get recent changes: {e}")
            return {"error": str(e)}
    
    def _add_watch_path(self, path: Path) -> Dict[str, Any]:
        """Add new path to monitoring"""
        try:
            if path not in self.watch_paths:
                self.watch_paths.append(path)
                
                if self.monitoring and path.exists():
                    self.observer.schedule(self.file_handler, str(path), recursive=True)
                    
                return {"status": "path_added", "path": str(path)}
            else:
                return {"status": "path_already_watched", "path": str(path)}
                
        except Exception as e:
            self.logger.error(f"Failed to add watch path: {e}")
            return {"error": str(e)}
    
    def _remove_watch_path(self, path: Path) -> Dict[str, Any]:
        """Remove path from monitoring"""
        try:
            if path in self.watch_paths:
                self.watch_paths.remove(path)
                # Note: Observer doesn't provide easy way to remove individual paths
                # Would need to restart observer to fully remove
                return {"status": "path_removed", "path": str(path), "note": "Restart required for full removal"}
            else:
                return {"status": "path_not_watched", "path": str(path)}
                
        except Exception as e:
            self.logger.error(f"Failed to remove watch path: {e}")
            return {"error": str(e)}