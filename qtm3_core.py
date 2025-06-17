#!/usr/bin/env python3
"""
Qwen Task Manager 3.0 - Hybrid Architecture
Combines behavioral activation with agentic design
"""

import sqlite3
import json
import uuid
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import textwrap

class TaskManagerCore:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.home() / "qtm3"
        self.db_path = self.base_dir / "core.db"
        self.prompts_dir = self.base_dir / "prompts"
        self.init_directories()
        self.init_database()
    
    def init_directories(self):
        """Create necessary directories"""
        self.base_dir.mkdir(exist_ok=True)
        (self.base_dir / "prompts").mkdir(exist_ok=True)
        (self.base_dir / "embeddings").mkdir(exist_ok=True)
        (self.base_dir / "archive").mkdir(exist_ok=True)
    
    def init_database(self):
        """Initialize SQLite with hybrid schema"""
        schema = """
        PRAGMA journal_mode=WAL;
        
        -- Core task table with behavioral fields
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'backlog',
            priority INTEGER,
            context TEXT,
            due TIMESTAMP,
            timer INTEGER,
            energy_required TEXT,
            energy_actual TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed TIMESTAMP,
            notes TEXT
        );
        
        -- Behavioral tracking
        CREATE TABLE IF NOT EXISTS reflections (
            id TEXT PRIMARY KEY,
            date DATE,
            content TEXT,
            energy_physical INTEGER,
            energy_mental INTEGER,
            energy_emotional INTEGER,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Vector embeddings for context
        CREATE VIRTUAL TABLE IF NOT EXISTS file_vectors USING fts5(
            path,
            content,
            embedding,
            tokenize='porter'
        );
        
        -- Task relationships
        CREATE TABLE IF NOT EXISTS task_dependencies (
            task_id TEXT,
            depends_on TEXT,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (depends_on) REFERENCES tasks(id)
        );
        
        -- Indexes for performance
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_tasks_due ON tasks(due);
        CREATE INDEX IF NOT EXISTS idx_reflections_date ON reflections(date);
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
    
    def create_task(self, title: str, description: str = None) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tasks (id, title, description) VALUES (?, ?, ?)",
                (task_id, title, description)
            )
        return task_id
    
    def get_tasks(self, status: str = None) -> List[Dict]:
        """Retrieve tasks by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM tasks"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += " ORDER BY priority DESC, due ASC"
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor]
    
    def update_task_status(self, task_id: str, status: str):
        """Update task status"""
        with sqlite3.connect(self.db_path) as conn:
            if status == 'done':
                conn.execute(
                    "UPDATE tasks SET status = ?, completed = CURRENT_TIMESTAMP WHERE id = ?",
                    (status, task_id)
                )
            else:
                conn.execute(
                    "UPDATE tasks SET status = ? WHERE id = ?",
                    (status, task_id)
                )


class QwenReasoning:
    """Handles all Qwen AI interactions"""
    
    def __init__(self, model: str = "qwen3:30b-a3b"):
        self.model = model
        self.ensure_ollama()
    
    def ensure_ollama(self):
        """Check if ollama is running"""
        try:
            subprocess.run(["pgrep", "-x", "ollama"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def think(self, prompt: str) -> str:
        """Run a /think prompt through Qwen"""
        full_prompt = f"/think\n{prompt}"
        result = subprocess.run(
            ["ollama", "run", self.model],
            input=full_prompt,
            text=True,
            capture_output=True
        )
        return result.stdout.strip()
    
    def clarify_tasks(self, raw_notes: str) -> List[Dict]:
        """Transform raw notes into structured tasks"""
        prompt = f"""
        You are a task clarification assistant. Transform these raw notes into clear, actionable tasks.
        
        Use SMART criteria:
        - Specific: Clear what needs to be done
        - Measurable: Define completion criteria
        - Achievable: Reasonable scope
        - Relevant: Include context
        - Time-bound: Estimate effort or deadline
        
        RAW NOTES:
        {raw_notes}
        
        Return as JSON array:
        [
            {{
                "title": "Clear action-oriented title",
                "description": "Additional context",
                "energy_required": "low|medium|high",
                "timer": estimated_minutes
            }}
        ]
        """
        
        response = self.think(prompt)
        try:
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            return json.loads(response[json_start:json_end])
        except:
            return [{"title": line.strip(), "description": "", "energy_required": "medium", "timer": 30} 
                    for line in raw_notes.split('\n') if line.strip()]
    
    def prioritize_tasks(self, tasks: List[Dict], context: Optional[str] = None) -> Dict:
        """Prioritize tasks with behavioral awareness"""
        tasks_json = json.dumps(tasks, indent=2)
        
        prompt = f"""
        You are a strategic task prioritization assistant with expertise in behavioral activation.
        
        Analyze these tasks considering:
        1. Impact vs Effort matrix
        2. Energy requirements (physical/mental/emotional)
        3. Time of day optimization
        4. Momentum building (start with quick wins)
        5. Context switching costs
        
        {"PROJECT CONTEXT: " + context if context else ""}
        
        TASKS:
        {tasks_json}
        
        Return a prioritization strategy as JSON:
        {{
            "immediate": [/* top 3 task IDs with reasons */],
            "quick_wins": [/* 15-minute tasks */],
            "deep_work": [/* high-focus tasks */],
            "batch": {{
                "context_name": [/* tasks to do together */]
            }},
            "defer": [/* tasks with reasons */],
            "energy_map": {{
                "morning": [/* high-energy tasks */],
                "afternoon": [/* medium-energy tasks */],
                "evening": [/* low-energy tasks */]
            }}
        }}
        """
        
        response = self.think(prompt)
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            return json.loads(response[json_start:json_end])
        except:
            return {"immediate": [], "quick_wins": [], "deep_work": [], "batch": {}, "defer": [], "energy_map": {}}
    
    def generate_reflection(self, completed_tasks: List[str], energy_levels: Dict[str, int]) -> str:
        """Generate behavioral activation reflection"""
        prompt = f"""
        You are a supportive reflection assistant practicing behavioral activation principles.
        
        Create a journal entry that:
        1. Acknowledges specific accomplishments
        2. Identifies energy patterns
        3. Celebrates effort over outcomes
        4. Notes what strategies worked
        5. Sets a compassionate intention for tomorrow
        
        COMPLETED TODAY:
        {chr(10).join('- ' + task for task in completed_tasks)}
        
        ENERGY LEVELS:
        Physical: {energy_levels.get('physical', 5)}/10
        Mental: {energy_levels.get('mental', 5)}/10
        Emotional: {energy_levels.get('emotional', 5)}/10
        
        Write a warm, encouraging reflection (2-3 paragraphs).
        """
        
        return self.think(prompt)


class PerceptionAgent:
    """Watches for changes and extracts context"""
    
    def __init__(self, watch_dirs: List[Path]):
        self.watch_dirs = watch_dirs
    
    def scan_projects(self) -> Dict[str, str]:
        """Scan project directories for context"""
        context = {}
        for watch_dir in self.watch_dirs:
            if watch_dir.exists():
                for file_path in watch_dir.rglob("*.md"):
                    try:
                        content = file_path.read_text()[:1000]  # First 1000 chars
                        project_name = file_path.parts[-2] if len(file_path.parts) > 1 else "general"
                        if project_name not in context:
                            context[project_name] = ""
                        context[project_name] += f"\n{file_path.name}: {content}"
                    except:
                        pass
        return context
    
    def extract_calendar_events(self) -> List[Dict]:
        """Extract events from calendar files"""
        # Placeholder for calendar integration
        return []


# CLI Interface functions
def create_prompts(base_dir: Path):
    """Create behavioral prompt templates"""
    prompts = {
        "clarify.qwen": textwrap.dedent("""
            /think
            Transform raw notes into clear, actionable tasks using SMART criteria.
            Consider energy requirements and optimal timing.
            
            INPUT:
            {{RAW_NOTES}}
        """),
        
        "prioritize.qwen": textwrap.dedent("""
            /think
            Prioritize tasks using behavioral activation principles.
            Consider energy, momentum, and context switching.
            
            TASKS:
            {{TASK_LIST}}
            
            CONTEXT:
            {{PROJECT_CONTEXT}}
        """),
        
        "reflect.qwen": textwrap.dedent("""
            /think
            Generate a compassionate reflection on today's progress.
            Focus on effort recognition and pattern identification.
            
            COMPLETED:
            {{COMPLETED_TASKS}}
            
            ENERGY:
            {{ENERGY_LEVELS}}
        """)
    }
    
    prompts_dir = base_dir / "prompts"
    prompts_dir.mkdir(exist_ok=True)
    
    for filename, content in prompts.items():
        (prompts_dir / filename).write_text(content)


def migrate_from_v1(old_dir: Path, new_core: TaskManagerCore):
    """Migrate from file-based v1 to database v3"""
    # Read old backlog
    backlog_file = old_dir / "tasks" / "backlog.txt"
    if backlog_file.exists():
        lines = backlog_file.read_text().split('\n')
        for line in lines:
            if line.strip().startswith('- [ ]'):
                title = line.replace('- [ ]', '').strip()
                new_core.create_task(title)
    
    print(f"Migrated {len(lines)} tasks from v1")