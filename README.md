# Qwen Local Task Manager

A Claude-inspired task management system powered by your local Qwen 3 model, implementing behavioral activation principles and AI-assisted organization.

## Features

- **AI-Powered Task Clarification**: Transform messy brain dumps into structured, actionable tasks
- **Strategic Prioritization**: Uses Qwen's reasoning to analyze impact, effort, and dependencies
- **Behavioral Activation**: Daily reflection prompts based on psychological principles
- **Local-First**: All data stays on your machine, processed by your local Qwen model
- **Claude-Style Thinking**: Leverages `/think` mode for deep analysis and synthesis

## Setup

1. **Prerequisites**:
   ```bash
   # Ensure Ollama is installed
   brew install ollama
   
   # Pull the Qwen model if not already present
   ollama pull qwen3:30b-a3b
   ```

2. **Make the script executable**:
   ```bash
   chmod +x run_task_manager.zsh
   ```

3. **Run the task manager**:
   ```bash
   ./run_task_manager.zsh
   ```

## Usage Guide

### Daily Workflow

1. **Morning Brain Dump** (Option 1: Capture)
   - Dump all thoughts, meetings, todos
   - Qwen will structure them into clear tasks

2. **Prioritize Your Day** (Option 2: Prioritize)
   - Analyzes your backlog
   - Identifies top 3 priorities
   - Groups quick wins
   - Assesses emotional/cognitive load

3. **Quick Adds Throughout the Day** (Option 3: Quick Add)
   - For urgent items that come up

4. **Evening Reflection** (Option 5: Reflect)
   - Log completed tasks
   - Get AI-generated journal entry
   - Track energy levels
   - Set tomorrow's intention

### Weekly Review

Run weekly to archive and analyze patterns:
```bash
./run_task_manager.zsh
# Choose option 6 (Archive) then 8 (Stats)
```

## File Structure

```
qwen_task_manager/
├── run_task_manager.zsh    # Main script
├── tasks/
│   ├── backlog.txt        # All pending tasks
│   ├── today.txt          # Today's priorities
│   └── reflections.txt    # Daily journals
├── prompts/
│   ├── clarify.qwen       # Task clarification prompt
│   ├── prioritize.qwen    # Prioritization prompt
│   ├── reflect.qwen       # Reflection prompt
│   ├── weekly_review.qwen # Weekly analysis
│   └── project_breakdown.qwen # Project decomposition
└── tasks/archive/         # Historical tasks
```

## Advanced Features

### Search (Option 7)
Find tasks across all files by keyword

### Stats Dashboard (Option 8)
View productivity metrics and trends

### Project Breakdown
For complex projects, use the project breakdown template:
```bash
# Edit prompts/project_breakdown.qwen with your project
# Then run through Ollama manually
```

## Customization

### Modify Prompts
Edit files in `prompts/` to customize AI behavior:
- Adjust tone and style
- Add domain-specific criteria
- Include personal productivity methods

### Change Model
To use a different model, edit `MODEL=` in the script:
```bash
MODEL="llama3.2:latest"  # For faster, lighter processing
```

## Tips

1. **Be Verbose in Captures**: The more context you provide, the better Qwen can organize
2. **Regular Reflections**: Daily reflections build momentum and self-awareness
3. **Weekly Archives**: Prevent backlog overwhelm by archiving completed cycles
4. **Energy Tracking**: Notice patterns in the energy scores from reflections

## Integration Ideas

- Add to `.zshrc`: `alias tasks='~/path/to/run_task_manager.zsh'`
- Cron job for daily reminders
- Hook into calendar systems
- Export to Markdown for note apps

## Based On

- Hilary Gridley's "How I Use AI as My Executive Function"
- Claude's thinking architecture
- Behavioral activation therapy principles
- Local-first AI philosophy

---

*Built with 🧠 by integrating Claude-style prompting with Qwen's local reasoning capabilities*