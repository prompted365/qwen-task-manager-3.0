#!/usr/bin/env zsh

# Qwen Local Task Manager
# Claude-inspired task management powered by local Qwen model

# Configuration
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKLOG="$BASE_DIR/tasks/backlog.txt"
TODAY="$BASE_DIR/tasks/today.txt"
REFLECT="$BASE_DIR/tasks/reflections.txt"
ARCHIVE="$BASE_DIR/tasks/archive"
PROMPT_DIR="$BASE_DIR/prompts"
MODEL="qwen3:30b-a3b"

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Ensure directories exist
mkdir -p "$BASE_DIR/tasks" "$BASE_DIR/prompts" "$ARCHIVE"

# Function: Check if ollama is running
check_ollama() {
    if ! pgrep -x "ollama" > /dev/null; then
        echo -e "${YELLOW}Starting Ollama service...${NC}"
        ollama serve &>/dev/null &
        sleep 3
    fi
}

# Function: Capture & Clarify Tasks
capture() {
    echo -e "${BLUE}✍️  Capture your tasks (Ctrl+D when done):${NC}"
    echo -e "${YELLOW}Tip: Brain dump everything - meetings, ideas, todos, thoughts${NC}\n"
    
    # Capture raw input
    cat > /tmp/raw_notes.txt
    
    # Process with Qwen
    echo -e "\n${GREEN}🤖 Processing with Qwen...${NC}"
    
    # Create prompt with template
    awk '/{{RAW_NOTES}}/ {
        while ((getline line < "/tmp/raw_notes.txt") > 0)
            print line
        next
    }
    {print}' "$PROMPT_DIR/clarify.qwen" > /tmp/clarify_prompt.txt
    
    # Run Qwen and append to backlog
    ollama run "$MODEL" < /tmp/clarify_prompt.txt | tee -a "$BACKLOG"
    
    echo -e "\n${GREEN}✅ Tasks added to backlog${NC}"
}

# Function: Prioritize Today's Work
prioritize() {
    if [[ ! -s "$BACKLOG" ]]; then
        echo -e "${RED}No tasks in backlog. Run 'capture' first.${NC}"
        return
    fi
    
    echo -e "${BLUE}🎯 Prioritizing tasks...${NC}"
    
    # Create prompt with backlog content
    awk -v backlog="$BACKLOG" '/{{BACKLOG_CONTENT}}/ {
        while ((getline line < backlog) > 0)
            print line
        next
    }
    {print}' "$PROMPT_DIR/prioritize.qwen" > /tmp/prioritize_prompt.txt
    
    # Run Qwen and save today's priorities
    ollama run "$MODEL" < /tmp/prioritize_prompt.txt | tee "$TODAY"
    
    echo -e "\n${GREEN}✅ Today's priorities saved${NC}"
}

# Function: Quick Task Add
quick_add() {
    echo -e "${BLUE}➕ Quick task (one line):${NC}"
    read -r task
    echo "- [ ] $task" >> "$BACKLOG"
    echo -e "${GREEN}✅ Added: $task${NC}"
}

# Function: View Tasks
view_tasks() {
    echo -e "${BLUE}📋 Current Tasks:${NC}\n"
    
    if [[ -f "$TODAY" ]] && [[ -s "$TODAY" ]]; then
        echo -e "${YELLOW}Today's Priorities:${NC}"
        cat "$TODAY"
        echo ""
    fi
    
    if [[ -f "$BACKLOG" ]] && [[ -s "$BACKLOG" ]]; then
        echo -e "${YELLOW}Backlog:${NC}"
        cat "$BACKLOG"
    else
        echo -e "${RED}No tasks in backlog${NC}"
    fi
}

# Function: Reflect on Completed Tasks
reflect() {
    echo -e "${BLUE}🪞 What tasks did you complete today? (Ctrl+D when done):${NC}"
    cat > /tmp/completed.txt
    
    if [[ ! -s /tmp/completed.txt ]]; then
        echo -e "${RED}No completed tasks entered${NC}"
        return
    fi
    
    # Add date to template
    DATE=$(date '+%Y-%m-%d')
    
    # Create prompt with completed tasks
    awk -v completed="/tmp/completed.txt" -v date="$DATE" '/{{COMPLETED_TASKS}}/ {
        while ((getline line < completed) > 0)
            print line
        next
    }
    /{{DATE}}/ {
        gsub(/{{DATE}}/, date)
    }
    {print}' "$PROMPT_DIR/reflect.qwen" > /tmp/reflect_prompt.txt
    
    # Run Qwen and append to reflections
    echo -e "\n${GREEN}🤖 Generating reflection...${NC}"
    ollama run "$MODEL" < /tmp/reflect_prompt.txt | tee -a "$REFLECT"
    
    echo -e "\n${GREEN}✅ Reflection saved${NC}"
}

# Function: Archive Old Tasks
archive_tasks() {
    ARCHIVE_DATE=$(date '+%Y%m%d')
    ARCHIVE_FILE="$ARCHIVE/tasks_$ARCHIVE_DATE.txt"
    
    echo -e "${BLUE}📦 Archiving current tasks...${NC}"
    
    {
        echo "=== ARCHIVED ON $(date) ==="
        echo "=== TODAY'S PRIORITIES ==="
        [[ -f "$TODAY" ]] && cat "$TODAY"
        echo -e "\n=== BACKLOG ==="
        [[ -f "$BACKLOG" ]] && cat "$BACKLOG"
        echo -e "\n=== END ARCHIVE ==="
    } > "$ARCHIVE_FILE"
    
    # Clear current files
    > "$TODAY"
    > "$BACKLOG"
    
    echo -e "${GREEN}✅ Tasks archived to: $ARCHIVE_FILE${NC}"
}

# Function: Search Tasks
search_tasks() {
    echo -e "${BLUE}🔍 Search term:${NC}"
    read -r search_term
    
    echo -e "\n${YELLOW}Search results:${NC}"
    grep -i "$search_term" "$BACKLOG" "$TODAY" "$REFLECT" 2>/dev/null | while IFS=: read -r file content; do
        basename=$(basename "$file")
        echo -e "${GREEN}[$basename]${NC} $content"
    done
}

# Function: Stats Dashboard
show_stats() {
    echo -e "${BLUE}📊 Task Manager Stats${NC}\n"
    
    total_backlog=$(grep -c "^\- \[" "$BACKLOG" 2>/dev/null || echo 0)
    total_completed=$(grep -c "✅" "$REFLECT" 2>/dev/null || echo 0)
    total_reflections=$(grep -c "^📝 Daily Reflection" "$REFLECT" 2>/dev/null || echo 0)
    
    echo -e "📋 Backlog items: ${YELLOW}$total_backlog${NC}"
    echo -e "✅ Completed (est): ${GREEN}$total_completed${NC}"
    echo -e "📝 Reflections: ${BLUE}$total_reflections${NC}"
    echo -e "📁 Archives: ${YELLOW}$(ls -1 "$ARCHIVE" 2>/dev/null | wc -l)${NC}"
}

# Main Menu
main_menu() {
    while true; do
        echo -e "\n${BLUE}=== Qwen Task Manager ===${NC}"
        echo "1) 📝 Capture Tasks"
        echo "2) 🎯 Prioritize Today"
        echo "3) ➕ Quick Add"
        echo "4) 📋 View Tasks"
        echo "5) 🪞 Reflect"
        echo "6) 📦 Archive"
        echo "7) 🔍 Search"
        echo "8) 📊 Stats"
        echo "9) 🚪 Exit"
        
        read -r "choice?Choose [1-9]: "
        
        case $choice in
            1) capture ;;
            2) prioritize ;;
            3) quick_add ;;
            4) view_tasks ;;
            5) reflect ;;
            6) archive_tasks ;;
            7) search_tasks ;;
            8) show_stats ;;
            9) echo -e "${GREEN}👋 Keep being awesome!${NC}"; break ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
    done
}

# Start
check_ollama
main_menu