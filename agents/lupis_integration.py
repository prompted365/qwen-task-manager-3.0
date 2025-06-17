"""
LUPIS Integration Layer
======================

Integration components for connecting LUPIS with existing QTM3 systems.
Provides bridge connectors for Component Registry, User Story Synthesiser,
Unix Socket Server, and external telemetry systems.
"""

import asyncio
import socket
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import zmq
import zmq.asyncio
from datetime import datetime, timezone

from config.lupis_config import LUPISConfig


@dataclass
class IntegrationEvent:
    """Event structure for cross-system communication."""
    source: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None


class QTM3Connector:
    """
    Connector for QTM3 Unix Socket Server communication.
    Handles bidirectional communication with existing QTM3 components.
    """
    
    def __init__(self, config: LUPISConfig):
        self.config = config
        self.socket_path = "/tmp/qtm3_lupis.sock"
        self.logger = logging.getLogger("lupis.qtm3_connector")
        self.connection: Optional[socket.socket] = None
        self.event_handlers: Dict[str, Callable] = {}
        
    async def connect(self) -> bool:
        """Establish connection to QTM3 Unix socket."""
        try:
            # Clean up any existing socket file
            if Path(self.socket_path).exists():
                Path(self.socket_path).unlink()
                
            self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.connection.setblocking(False)
            
            # Try to connect to existing QTM3 socket
            try:
                await asyncio.get_event_loop().sock_connect(
                    self.connection, 
                    "/tmp/qtm3_main.sock"
                )
                self.logger.info("Connected to QTM3 main socket")
                return True
            except FileNotFoundError:
                self.logger.warning("QTM3 main socket not found, creating standalone")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to connect to QTM3: {e}")
            return False
    
    async def send_event(self, event: IntegrationEvent) -> bool:
        """Send event to QTM3 system."""
        if not self.connection:
            return False
            
        try:
            message = json.dumps(asdict(event), default=str)
            await asyncio.get_event_loop().sock_sendall(
                self.connection, 
                message.encode() + b'\n'
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to send event: {e}")
            return False
    
    async def listen_for_events(self) -> None:
        """Listen for incoming events from QTM3."""
        if not self.connection:
            return
            
        buffer = b""
        while True:
            try:
                data = await asyncio.get_event_loop().sock_recv(self.connection, 1024)
                if not data:
                    break
                    
                buffer += data
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    try:
                        event_data = json.loads(line.decode())
                        event = IntegrationEvent(**event_data)
                        await self._handle_event(event)
                    except Exception as e:
                        self.logger.error(f"Failed to process event: {e}")
                        
            except Exception as e:
                self.logger.error(f"Error listening for events: {e}")
                break
    
    async def _handle_event(self, event: IntegrationEvent) -> None:
        """Handle incoming event from QTM3."""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            try:
                await handler(event)
            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")
    
    def register_handler(self, event_type: str, handler: Callable) -> None:
        """Register event handler for specific event type."""
        self.event_handlers[event_type] = handler
    
    async def disconnect(self) -> None:
        """Cleanup connection."""
        if self.connection:
            self.connection.close()
            self.connection = None


class ComponentRegistryIntegration:
    """
    Integration with QTM3 Component Registry.
    Synchronizes component discovery and health monitoring.
    """
    
    def __init__(self, config: LUPISConfig, qtm3_connector: QTM3Connector):
        self.config = config
        self.qtm3_connector = qtm3_connector
        self.logger = logging.getLogger("lupis.component_registry")
        self.known_components: Dict[str, Dict[str, Any]] = {}
        
        # Register event handlers
        qtm3_connector.register_handler("component_registered", self._on_component_registered)
        qtm3_connector.register_handler("component_health", self._on_component_health)
        qtm3_connector.register_handler("component_removed", self._on_component_removed)
    
    async def discover_components(self) -> List[Dict[str, Any]]:
        """Request component discovery from registry."""
        event = IntegrationEvent(
            source="lupis",
            event_type="discover_components",
            payload={},
            timestamp=datetime.now(timezone.utc)
        )
        
        await self.qtm3_connector.send_event(event)
        
        # Return current known components
        return list(self.known_components.values())
    
    async def _on_component_registered(self, event: IntegrationEvent) -> None:
        """Handle component registration event."""
        component_data = event.payload
        component_id = component_data.get("id")
        
        if component_id:
            self.known_components[component_id] = component_data
            self.logger.info(f"Component registered: {component_id}")
    
    async def _on_component_health(self, event: IntegrationEvent) -> None:
        """Handle component health update."""
        component_id = event.payload.get("component_id")
        health_data = event.payload.get("health")
        
        if component_id in self.known_components:
            self.known_components[component_id]["last_health"] = health_data
            self.known_components[component_id]["last_seen"] = event.timestamp
    
    async def _on_component_removed(self, event: IntegrationEvent) -> None:
        """Handle component removal."""
        component_id = event.payload.get("component_id")
        if component_id in self.known_components:
            del self.known_components[component_id]
            self.logger.info(f"Component removed: {component_id}")
    
    async def get_component_health(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Get health status for specific component."""
        component = self.known_components.get(component_id)
        if component:
            return component.get("last_health")
        return None
    
    async def get_component_metrics(self) -> Dict[str, Any]:
        """Get overall component registry metrics."""
        total_components = len(self.known_components)
        healthy_components = sum(
            1 for comp in self.known_components.values()
            if comp.get("last_health", {}).get("status") == "healthy"
        )
        
        return {
            "total_components": total_components,
            "healthy_components": healthy_components,
            "unhealthy_components": total_components - healthy_components,
            "health_ratio": healthy_components / total_components if total_components > 0 else 0
        }


class USSIntegration:
    """
    Integration with User Story Synthesiser for story-driven optimization.
    Enables LUPIS to create and manage user stories based on system observations.
    """
    
    def __init__(self, config: LUPISConfig, qtm3_connector: QTM3Connector):
        self.config = config
        self.qtm3_connector = qtm3_connector
        self.logger = logging.getLogger("lupis.uss_integration")
        self.active_stories: Dict[str, Dict[str, Any]] = {}
        
        # Register event handlers
        qtm3_connector.register_handler("story_created", self._on_story_created)
        qtm3_connector.register_handler("story_updated", self._on_story_updated)
        qtm3_connector.register_handler("story_completed", self._on_story_completed)
    
    async def create_optimization_story(self, 
                                      optimization_data: Dict[str, Any]) -> Optional[str]:
        """Create user story from optimization proposal."""
        story_payload = {
            "type": "optimization",
            "title": f"System Optimization: {optimization_data.get('title', 'Untitled')}",
            "description": optimization_data.get("description", ""),
            "priority": optimization_data.get("priority", "medium"),
            "estimated_effort": optimization_data.get("effort_estimate", "unknown"),
            "expected_roi": optimization_data.get("roi_score", 0),
            "automation_eligible": optimization_data.get("automation_eligible", False),
            "drift_context": optimization_data.get("drift_analysis", {}),
            "source": "lupis_optimization"
        }
        
        event = IntegrationEvent(
            source="lupis",
            event_type="create_story",
            payload=story_payload,
            timestamp=datetime.now(timezone.utc)
        )
        
        success = await self.qtm3_connector.send_event(event)
        if success:
            self.logger.info("Optimization story creation requested")
            return optimization_data.get("id")
        return None
    
    async def create_drift_story(self, drift_analysis: Dict[str, Any]) -> Optional[str]:
        """Create user story from drift analysis."""
        story_payload = {
            "type": "maintenance",
            "title": f"Component Drift: {drift_analysis.get('component_name', 'Unknown')}",
            "description": f"Detected drift in component with score: {drift_analysis.get('total_score', 0)}",
            "priority": self._calculate_drift_priority(drift_analysis),
            "drift_details": drift_analysis,
            "recommended_actions": drift_analysis.get("recommendations", []),
            "source": "lupis_drift_detection"
        }
        
        event = IntegrationEvent(
            source="lupis",
            event_type="create_story",
            payload=story_payload,
            timestamp=datetime.now(timezone.utc)
        )
        
        success = await self.qtm3_connector.send_event(event)
        if success:
            self.logger.info(f"Drift story created for component: {drift_analysis.get('component_name')}")
            return drift_analysis.get("component_id")
        return None
    
    def _calculate_drift_priority(self, drift_analysis: Dict[str, Any]) -> str:
        """Calculate story priority based on drift severity."""
        score = drift_analysis.get("total_score", 0)
        
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"
    
    async def _on_story_created(self, event: IntegrationEvent) -> None:
        """Handle story creation confirmation."""
        story_data = event.payload
        story_id = story_data.get("id")
        
        if story_id:
            self.active_stories[story_id] = story_data
            self.logger.info(f"Story created: {story_id}")
    
    async def _on_story_updated(self, event: IntegrationEvent) -> None:
        """Handle story update."""
        story_id = event.payload.get("id")
        if story_id in self.active_stories:
            self.active_stories[story_id].update(event.payload)
    
    async def _on_story_completed(self, event: IntegrationEvent) -> None:
        """Handle story completion."""
        story_id = event.payload.get("id")
        if story_id in self.active_stories:
            completed_story = self.active_stories.pop(story_id)
            self.logger.info(f"Story completed: {story_id}")
            
            # If this was an optimization story, update success metrics
            if completed_story.get("source") == "lupis_optimization":
                await self._track_optimization_success(completed_story)
    
    async def _track_optimization_success(self, story: Dict[str, Any]) -> None:
        """Track optimization story completion for learning."""
        success_event = IntegrationEvent(
            source="lupis",
            event_type="optimization_completed",
            payload={
                "story_id": story.get("id"),
                "expected_roi": story.get("expected_roi", 0),
                "completion_time": datetime.now(timezone.utc),
                "story_data": story
            },
            timestamp=datetime.now(timezone.utc)
        )
        
        await self.qtm3_connector.send_event(success_event)
    
    async def get_active_stories(self) -> List[Dict[str, Any]]:
        """Get list of active LUPIS-generated stories."""
        return list(self.active_stories.values())


class TelemetryIntegration:
    """
    Integration for external telemetry systems via ZeroMQ.
    Collects metrics from external monitoring systems.
    """
    
    def __init__(self, config: LUPISConfig):
        self.config = config
        self.logger = logging.getLogger("lupis.telemetry_integration")
        self.context = zmq.asyncio.Context()
        self.subscriber = None
        self.publisher = None
        self.running = False
        
    async def start(self) -> bool:
        """Start telemetry integration."""
        try:
            # Setup subscriber for incoming metrics
            self.subscriber = self.context.socket(zmq.SUB)
            self.subscriber.connect(f"tcp://localhost:{self.config.telemetry.zmq_port}")
            self.subscriber.setsockopt(zmq.SUBSCRIBE, b"lupis.")
            
            # Setup publisher for outgoing events
            self.publisher = self.context.socket(zmq.PUB)
            self.publisher.bind(f"tcp://*:{self.config.telemetry.zmq_port + 1}")
            
            self.running = True
            self.logger.info("Telemetry integration started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start telemetry integration: {e}")
            return False
    
    async def listen_for_metrics(self) -> None:
        """Listen for incoming telemetry data."""
        while self.running and self.subscriber:
            try:
                # Non-blocking receive with timeout
                topic, message = await self.subscriber.recv_multipart(zmq.NOBLOCK)
                
                metric_data = json.loads(message.decode())
                await self._process_metric(topic.decode(), metric_data)
                
            except zmq.Again:
                # No message available
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error receiving telemetry: {e}")
                await asyncio.sleep(1)
    
    async def _process_metric(self, topic: str, data: Dict[str, Any]) -> None:
        """Process incoming metric data."""
        self.logger.debug(f"Received metric: {topic}")
        
        # Add processing logic based on metric type
        if topic.startswith("lupis.performance"):
            await self._handle_performance_metric(data)
        elif topic.startswith("lupis.error"):
            await self._handle_error_metric(data)
        elif topic.startswith("lupis.user"):
            await self._handle_user_metric(data)
    
    async def _handle_performance_metric(self, data: Dict[str, Any]) -> None:
        """Handle performance metrics."""
        # Implementation for performance metric processing
        pass
    
    async def _handle_error_metric(self, data: Dict[str, Any]) -> None:
        """Handle error metrics."""
        # Implementation for error metric processing
        pass
    
    async def _handle_user_metric(self, data: Dict[str, Any]) -> None:
        """Handle user behavior metrics."""
        # Implementation for user metric processing
        pass
    
    async def publish_lupis_event(self, event_type: str, data: Dict[str, Any]) -> bool:
        """Publish LUPIS event to telemetry system."""
        if not self.publisher:
            return False
            
        try:
            topic = f"lupis.{event_type}"
            message = json.dumps(data, default=str)
            
            await self.publisher.send_multipart([
                topic.encode(),
                message.encode()
            ])
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish event: {e}")
            return False
    
    async def stop(self) -> None:
        """Stop telemetry integration."""
        self.running = False
        
        if self.subscriber:
            self.subscriber.close()
        if self.publisher:
            self.publisher.close()
            
        self.context.term()
        self.logger.info("Telemetry integration stopped")


class LUPISIntegrationManager:
    """
    Central manager for all LUPIS integrations.
    Coordinates between different integration components.
    """
    
    def __init__(self, config: LUPISConfig):
        self.config = config
        self.logger = logging.getLogger("lupis.integration_manager")
        
        # Initialize integration components
        self.qtm3_connector = QTM3Connector(config)
        self.component_registry = ComponentRegistryIntegration(config, self.qtm3_connector)
        self.uss_integration = USSIntegration(config, self.qtm3_connector)
        self.telemetry_integration = TelemetryIntegration(config)
        
        self.running = False
    
    async def start_all_integrations(self) -> bool:
        """Start all integration components."""
        try:
            # Start QTM3 connection
            qtm3_connected = await self.qtm3_connector.connect()
            if not qtm3_connected:
                self.logger.warning("QTM3 connection failed, running in standalone mode")
            
            # Start telemetry integration
            telemetry_started = await self.telemetry_integration.start()
            if not telemetry_started:
                self.logger.warning("Telemetry integration failed to start")
            
            self.running = True
            self.logger.info("LUPIS integration manager started")
            
            # Start background tasks
            if qtm3_connected:
                asyncio.create_task(self.qtm3_connector.listen_for_events())
            
            if telemetry_started:
                asyncio.create_task(self.telemetry_integration.listen_for_metrics())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start integrations: {e}")
            return False
    
    async def stop_all_integrations(self) -> None:
        """Stop all integration components."""
        self.running = False
        
        await self.qtm3_connector.disconnect()
        await self.telemetry_integration.stop()
        
        self.logger.info("LUPIS integration manager stopped")
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        return {
            "qtm3_connected": self.qtm3_connector.connection is not None,
            "telemetry_running": self.telemetry_integration.running,
            "active_stories": len(await self.uss_integration.get_active_stories()),
            "known_components": len(self.component_registry.known_components),
            "integration_manager_running": self.running
        }
    
    async def create_optimization_workflow(self, optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete optimization workflow across all integrations."""
        results = {}
        
        # Create user story
        story_id = await self.uss_integration.create_optimization_story(optimization_data)
        results["story_created"] = story_id is not None
        results["story_id"] = story_id
        
        # Publish telemetry event
        telemetry_published = await self.telemetry_integration.publish_lupis_event(
            "optimization_proposed",
            optimization_data
        )
        results["telemetry_published"] = telemetry_published
        
        # Send QTM3 notification
        if self.qtm3_connector.connection:
            notification_event = IntegrationEvent(
                source="lupis",
                event_type="optimization_workflow_started",
                payload={
                    "optimization_id": optimization_data.get("id"),
                    "story_id": story_id,
                    "priority": optimization_data.get("priority")
                },
                timestamp=datetime.now(timezone.utc)
            )
            results["qtm3_notified"] = await self.qtm3_connector.send_event(notification_event)
        
        return results