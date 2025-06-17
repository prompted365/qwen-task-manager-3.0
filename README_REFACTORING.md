# Qwen Task Manager Evolution

## Version Comparison

### v1: Behavioral Activation Focus
- **Philosophy**: Claude-inspired prompting with psychological grounding
- **Storage**: Simple file-based (backlog.txt, reflections.txt)
- **Strengths**: Rich UX, immediate usability, behavioral patterns
- **Limitations**: No context awareness, manual organization

### v2: Agentic Architecture (Colleague's Vision)
- **Philosophy**: Ubiquity OS-aligned micro-agents
- **Storage**: SQLite with vector embeddings
- **Strengths**: Auto-tagging, file watching, calendar sync
- **Limitations**: Complex setup, less focus on human psychology

### v3: Hybrid Optimization ✨
- **Philosophy**: Best of both worlds - behavioral intelligence + technical sophistication
- **Storage**: SQLite with behavioral fields + vector context
- **New Features**:
  - 🧠 AI reasoning with emotional intelligence
  - 📊 Context-aware prioritization
  - 🔄 Automatic project tagging
  - ⏰ Timer integration with reflection triggers
  - 🔍 Semantic search across tasks
  - 📈 Energy pattern analysis

## Refactoring Plan

### Phase 1: Core Migration ✅
1. **Unified Data Model**
   - SQLite schema combining task data + behavioral metrics
   - Vector embeddings for semantic search
   - Preserved reflection history

2. **Hybrid Reasoning**
   - Qwen `/think` mode for all major decisions
   - Behavioral prompts integrated into agentic flow
   - Context extraction from project files

3. **Enhanced CLI**
   - fzf-powered menus with rich colors
   - Quick capture modes
   - Seamless migration path

### Phase 2: Intelligence Layer (Next Steps)
1. **Smart Agents**
   - File watcher for auto-context updates
   - Calendar bidirectional sync
   - Energy-based scheduling optimizer

2. **Advanced Features**
   - Task dependency graphs
   - Momentum tracking
   - Collaborative task sharing

3. **Integrations**
   - VS Code extension
   - Mobile companion app
   - Voice capture via Whisper

## Installation

```bash
# Quick install
chmod +x install_v3.sh
./install_v3.sh

# Manual install
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/toolbox/qwen_task_manager
python3 qtm3_core.py  # Initializes database
chmod +x qtm3
ln -s $(pwd)/qtm3 ~/.local/bin/qtm3
```

## Migration from v1/v2

```bash
# Automatic migration during install
./install_v3.sh  # Will detect and offer migration

# Manual migration
python3 migrate_to_v3.py
```

## Architecture Benefits

### From v1 (Behavioral)
- ✅ Preserved: Rich prompts, energy tracking, reflection patterns
- ✅ Enhanced: Now with automatic context and smart scheduling

### From v2 (Agentic)
- ✅ Preserved: Modular architecture, vector search, system integration  
- ✅ Enhanced: Now with psychological intelligence and better UX

### Unique to v3
- 🎯 **Behavioral Vector Space**: Tasks embedded by both content AND energy patterns
- 🤖 **Adaptive Prompting**: Templates adjust based on your project corpus
- 📊 **Holistic Analytics**: Tracks both productivity metrics AND wellbeing
- 🔄 **Seamless Workflow**: One unified interface for all operations

## Usage Examples

```bash
# Morning routine
qtm3                    # Launch interactive mode
→ Brain Dump           # Empty your mind
→ Prioritize           # Get AI-powered schedule

# Throughout the day
qtm3 add "Call Sarah about project"
qtm3 today             # Check current priorities
qtm3 timer abc123 45   # Set 45-min focus block

# Evening reflection
qtm3 reflect           # Guided behavioral reflection

# Weekly analysis
qtm3                   # Launch interactive
→ Weekly Review        # See patterns and insights
```

## Technical Stack

- **Core**: Python 3.8+ with SQLite
- **AI**: Qwen 3 30B via Ollama
- **UI**: Zsh + fzf + rich terminal colors
- **Search**: FTS5 full-text search + vector similarity
- **Integration**: Calendar (ics), Timers (at/cron), File watching

## Future Roadmap

1. **Q3 2025**: Web dashboard with task analytics
2. **Q4 2025**: Multi-user collaboration features
3. **Q1 2026**: Plugin ecosystem for custom workflows

---

The hybrid v3 combines the **heart** of behavioral activation with the **brain** of agentic architecture, creating a task manager that's both emotionally intelligent and technically sophisticated.