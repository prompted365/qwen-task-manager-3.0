#!/usr/bin/env python3
"""
QTM3 Service Splitter
Refactors monolithic core into modular agents for Week 2
"""

from abc import ABC, abstractmethod
from pathlib import Path
import json
import socket
import threading
from typing import Dict, Any, Optional
import logging

# Base Agent Interface
class Agent(ABC):
    """Base class for all QTM3 agents"""
    
    def __init__(self, name: str, socket_path: Path = None):
        self.name = name
        self.socket_path = socket_path or Path(f"/tmp/qtm3_{name}.sock")
        self.logger = logging.getLogger(f"qtm3.{name}")
        self.running = False
    
    @abstractmethod
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and return response"""
        pass
    
    def start_server(self):
        """Start Unix socket server for IPC"""
        if self.socket_path.exists():
            self.socket_path.unlink()
        
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.socket_path))
        server.listen(1)
        self.running = True
        
        self.logger.info(f"{self.name} agent listening on {self.socket_path}")
        
        while self.running:
            try:
                conn, _ = server.accept()
                threading.Thread(target=self._handle_connection, args=(conn,)).start()
            except KeyboardInterrupt:
                break
        
        server.close()
        self.socket_path.unlink()
    
    def _handle_connection(self, conn):
        """Handle individual client connection"""
        try:
            data = conn.recv(4096)
            message = json.loads(data.decode())
            
            response = self.handle_message(message)
            conn.send(json.dumps(response).encode())
        except Exception as e:
            error_response = {"error": str(e)}
            conn.send(json.dumps(error_response).encode())
        finally:
            conn.close()
    
    def send_to_agent(self, target_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to another agent"""
        target_socket = Path(f"/tmp/qtm3_{target_agent}.sock")
        
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(target_socket))
        
        client.send(json.dumps(message).encode())
        response = client.recv(4096)
        client.close()
        
        return json.loads(response.decode())


# Perception Agent
class PerceptionAgent(Agent):
    """Handles file watching, calendar polling, input capture"""
    
    def __init__(self):
        super().__init__("perception")
        self.watch_dirs = [Path.home() / "projects"]
        self.perception_locked = True
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        
        if action == "scan_files":
            return self._scan_files(message.get("path"))
        elif action == "watch_calendar":
            return self._watch_calendar()
        elif action == "capture_input":
            return self._capture_input(message.get("input"))
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _scan_files(self, path: str) -> Dict[str, Any]:
        """Scan files and return perception-locked data"""
        scan_path = Path(path) if path else self.watch_dirs[0]
        results = []
        
        for file_path in scan_path.rglob("*.md"):
            if self.perception_locked:
                # Return only hash and metadata
                results.append({
                    "hash": hash(str(file_path)),
                    "type": "markdown",
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
            else:
                # Full content (only if unlocked)
                results.append({
                    "path": str(file_path),
                    "content": file_path.read_text()[:500]
                })
        
        return {"files": results}
    
    def _watch_calendar(self) -> Dict[str, Any]:
        """Poll calendar files for changes"""
        # Placeholder for calendar integration
        return {"events": []}
    
    def _capture_input(self, raw_input: str) -> Dict[str, Any]:
        """Process raw user input"""
        return {
            "captured": True,
            "hash": hash(raw_input),
            "length": len(raw_input),
            "timestamp": str(Path.home())  # Would be datetime
        }


# Memory Agent
class MemoryAgent(Agent):
    """Handles all database operations"""
    
    def __init__(self, db_path: Path = None):
        super().__init__("memory")
        self.db_path = db_path or Path.home() / "qtm3" / "core.db"
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        
        if action == "create_task":
            return self._create_task(message.get("task"))
        elif action == "get_tasks":
            return self._get_tasks(message.get("filter"))
        elif action == "update_task":
            return self._update_task(message.get("task_id"), message.get("updates"))
        elif action == "store_reflection":
            return self._store_reflection(message.get("reflection"))
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _create_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create new task in database"""
        # Would use actual database operations
        return {"task_id": "mock-uuid", "created": True}
    
    def _get_tasks(self, filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve tasks with optional filtering"""
        # Would query actual database
        return {"tasks": []}
    
    def _update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing task"""
        return {"updated": True}
    
    def _store_reflection(self, reflection: Dict[str, Any]) -> Dict[str, Any]:
        """Store daily reflection"""
        return {"stored": True}


# Reasoning Agent
class ReasoningAgent(Agent):
    """Handles all Qwen AI interactions"""
    
    def __init__(self, model: str = "qwen3:30b-a3b"):
        super().__init__("reasoning")
        self.model = model
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        
        if action == "clarify_tasks":
            return self._clarify_tasks(message.get("raw_notes"))
        elif action == "prioritize":
            return self._prioritize(message.get("tasks"))
        elif action == "generate_reflection":
            return self._generate_reflection(message.get("completed"))
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _clarify_tasks(self, raw_notes: str) -> Dict[str, Any]:
        """Transform raw notes into structured tasks"""
        # Would call Qwen with /think prompt
        return {
            "tasks": [
                {"title": "Parsed task", "energy": "medium", "timer": 30}
            ]
        }
    
    def _prioritize(self, tasks: list) -> Dict[str, Any]:
        """Generate prioritization strategy"""
        return {
            "immediate": [],
            "quick_wins": [],
            "deep_work": [],
            "defer": []
        }
    
    def _generate_reflection(self, completed_tasks: list) -> Dict[str, Any]:
        """Generate behavioral reflection"""
        return {
            "reflection": "Today was productive...",
            "energy_assessment": {"physical": 7, "mental": 6, "emotional": 8}
        }


# Exchange Agent
class ExchangeAgent(Agent):
    """Handles external system interactions (timers, calendar, notifications)"""
    
    def __init__(self):
        super().__init__("exchange")
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        action = message.get("action")
        
        if action == "set_timer":
            return self._set_timer(message.get("minutes"), message.get("task_id"))
        elif action == "write_calendar":
            return self._write_calendar(message.get("event"))
        elif action == "send_notification":
            return self._send_notification(message.get("notification"))
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _set_timer(self, minutes: int, task_id: str) -> Dict[str, Any]:
        """Set system timer for task"""
        # Would use 'at' command or systemd timer
        return {"timer_set": True, "minutes": minutes}
    
    def _write_calendar(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Write event to calendar file"""
        # Would write .ics format
        return {"calendar_updated": True}
    
    def _send_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Send desktop notification"""
        # Would use osascript on macOS or notify-send on Linux
        return {"notification_sent": True}


# Agent Orchestrator
class AgentOrchestrator:
    """Coordinates communication between agents"""
    
    def __init__(self):
        self.agents = {
            "perception": PerceptionAgent(),
            "memory": MemoryAgent(),
            "reasoning": ReasoningAgent(),
            "exchange": ExchangeAgent()
        }
    
    def start_all_agents(self):
        """Start all agents in separate threads"""
        threads = []
        for name, agent in self.agents.items():
            thread = threading.Thread(target=agent.start_server)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        print("All agents started. Press Ctrl+C to stop.")
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\nStopping all agents...")
    
    def capture_task_flow(self, raw_input: str) -> str:
        """Example flow: capture -> clarify -> store -> prioritize"""
        
        # 1. Perception captures input
        perception_result = self.send_message("perception", {
            "action": "capture_input",
            "input": raw_input
        })
        
        # 2. Reasoning clarifies into tasks
        reasoning_result = self.send_message("reasoning", {
            "action": "clarify_tasks",
            "raw_notes": raw_input
        })
        
        # 3. Memory stores tasks
        for task in reasoning_result.get("tasks", []):
            self.send_message("memory", {
                "action": "create_task",
                "task": task
            })
        
        # 4. Get all tasks for prioritization
        all_tasks = self.send_message("memory", {
            "action": "get_tasks",
            "filter": {"status": "backlog"}
        })
        
        # 5. Reasoning prioritizes
        priority_result = self.send_message("reasoning", {
            "action": "prioritize",
            "tasks": all_tasks.get("tasks", [])
        })
        
        return f"Captured {len(reasoning_result.get('tasks', []))} tasks"
    
    def send_message(self, agent_name: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to specific agent"""
        socket_path = Path(f"/tmp/qtm3_{agent_name}.sock")
        
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(str(socket_path))
        
        client.send(json.dumps(message).encode())
        response = client.recv(4096)
        client.close()
        
        return json.loads(response.decode())


if __name__ == "__main__":
    # Example: Start all agents
    orchestrator = AgentOrchestrator()
    orchestrator.start_all_agents()