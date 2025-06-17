#!/usr/bin/env python3
"""
Migration script from QTM v1/v2 to v3
Preserves tasks, reflections, and behavioral data
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import sys

def migrate_v1_to_v3(v1_dir: Path, v3_dir: Path):
    """Migrate from file-based v1 to SQLite v3"""
    
    # Import v3 core
    sys.path.insert(0, str(v1_dir))
    from qtm3_core import TaskManagerCore
    
    # Initialize v3
    core = TaskManagerCore(v3_dir)
    
    print("🔄 Migrating from v1 to v3...")
    
    # Migrate tasks
    backlog_file = v1_dir / "tasks" / "backlog.txt"
    migrated_tasks = 0
    
    if backlog_file.exists():
        lines = backlog_file.read_text().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('- [ ]'):
                title = line[5:].strip()
                core.create_task(title)
                migrated_tasks += 1
            elif line.startswith('- [x]'):
                title = line[5:].strip()
                task_id = core.create_task(title)
                core.update_task_status(task_id, 'done')
                migrated_tasks += 1
    
    print(f"  ✅ Migrated {migrated_tasks} tasks")
    
    # Migrate reflections
    reflections_file = v1_dir / "tasks" / "reflections.txt"
    migrated_reflections = 0
    
    if reflections_file.exists():
        content = reflections_file.read_text()
        # Simple parsing - look for date patterns
        sections = content.split('📝 Daily Reflection')
        
        with sqlite3.connect(core.db_path) as conn:
            for section in sections[1:]:  # Skip first empty
                lines = section.strip().split('\n')
                if lines:
                    # Try to extract date from first line
                    date_str = lines[0].strip(' -')
                    try:
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        reflection_content = '\n'.join(lines[1:])
                        
                        # Extract energy if present
                        energy_physical = 5
                        energy_mental = 5
                        energy_emotional = 5
                        
                        for line in lines:
                            if 'Physical:' in line:
                                try:
                                    energy_physical = int(line.split(':')[1].strip().split('/')[0])
                                except:
                                    pass
                            elif 'Mental:' in line:
                                try:
                                    energy_mental = int(line.split(':')[1].strip().split('/')[0])
                                except:
                                    pass
                            elif 'Emotional:' in line:
                                try:
                                    energy_emotional = int(line.split(':')[1].strip().split('/')[0])
                                except:
                                    pass
                        
                        conn.execute("""
                            INSERT INTO reflections 
                            (id, date, content, energy_physical, energy_mental, energy_emotional)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            str(uuid.uuid4()),
                            date,
                            reflection_content,
                            energy_physical,
                            energy_mental,
                            energy_emotional
                        ))
                        migrated_reflections += 1
                    except Exception as e:
                        print(f"  ⚠️  Could not parse reflection: {e}")
    
    print(f"  ✅ Migrated {migrated_reflections} reflections")
    
    # Copy prompts
    v1_prompts = v1_dir / "prompts"
    v3_prompts = v3_dir / "prompts"
    
    if v1_prompts.exists():
        v3_prompts.mkdir(exist_ok=True)
        for prompt_file in v1_prompts.glob("*.qwen"):
            (v3_prompts / prompt_file.name).write_text(prompt_file.read_text())
        print(f"  ✅ Copied {len(list(v1_prompts.glob('*.qwen')))} prompts")
    
    print("\n✨ Migration complete!")
    print(f"   New database: {core.db_path}")
    print(f"   Run 'qtm3' to start using v3")


def check_existing_installation():
    """Check for existing QTM installations"""
    v1_path = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "toolbox" / "qwen_task_manager"
    v2_path = Path.home() / "qtm"
    v3_path = Path.home() / "qtm3"
    
    installations = []
    
    if v1_path.exists():
        installations.append(("v1 (file-based)", v1_path))
    if v2_path.exists():
        installations.append(("v2 (agentic)", v2_path))
    if v3_path.exists():
        installations.append(("v3 (hybrid)", v3_path))
    
    return installations


if __name__ == "__main__":
    import uuid  # Import here for the migration
    
    print("🔍 Checking for existing QTM installations...")
    
    installations = check_existing_installation()
    
    if not installations:
        print("❌ No existing QTM installations found")
        sys.exit(1)
    
    print("\nFound installations:")
    for i, (version, path) in enumerate(installations):
        print(f"  {i+1}. {version} at {path}")
    
    if len(installations) > 1:
        choice = input("\nWhich version to migrate from? (number): ")
        try:
            idx = int(choice) - 1
            source_version, source_path = installations[idx]
        except:
            print("❌ Invalid choice")
            sys.exit(1)
    else:
        source_version, source_path = installations[0]
    
    v3_path = Path.home() / "qtm3"
    
    print(f"\n📦 Migrating from {source_version} to v3...")
    print(f"   Source: {source_path}")
    print(f"   Target: {v3_path}")
    
    confirm = input("\nProceed? (y/N): ")
    if confirm.lower() != 'y':
        print("❌ Migration cancelled")
        sys.exit(0)
    
    # Run migration
    if "v1" in source_version:
        migrate_v1_to_v3(source_path, v3_path)
    else:
        print("❌ Migration from v2 not yet implemented")
        # TODO: Implement v2 migration