#!/usr/bin/env bash

# Qwen Task Manager 3.0 - Hybrid Installation Script

set -e

echo "🚀 Installing Qwen Task Manager 3.0 (Hybrid Architecture)"
echo "======================================================="

# Check dependencies
echo "📋 Checking dependencies..."

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install:"
    echo "   brew install ollama"
    exit 1
fi

# Check fzf
if ! command -v fzf &> /dev/null; then
    echo "⚠️  fzf not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install fzf
    else
        echo "❌ Please install fzf manually"
        exit 1
    fi
fi

# Check SQLite
if ! command -v sqlite3 &> /dev/null; then
    echo "❌ SQLite3 not found. Please install:"
    echo "   brew install sqlite"
    exit 1
fi

echo "✅ All dependencies satisfied"

# Check for Qwen model
echo -e "\n📦 Checking Qwen model..."
if ! ollama list | grep -q "qwen3:30b-a3b"; then
    echo "📥 Pulling Qwen model (18GB - this will take a while)..."
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ollama pull qwen3:30b-a3b
    else
        echo "⚠️  Skipping model download. You'll need to run: ollama pull qwen3:30b-a3b"
    fi
else
    echo "✅ Qwen model already installed"
fi

# Setup directories
INSTALL_DIR="$HOME/qtm3"
BIN_DIR="$HOME/.local/bin"

echo -e "\n📂 Setting up directories..."
mkdir -p "$INSTALL_DIR"/{prompts,embeddings,archive}
mkdir -p "$BIN_DIR"

# Copy files
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/qtm3_core.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/qtm3" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/qtm3"

# Create symlink
ln -sf "$INSTALL_DIR/qtm3" "$BIN_DIR/qtm3"

# Initialize database and prompts
echo -e "\n🗄️  Initializing database..."
cd "$INSTALL_DIR"
python3 -c "
from qtm3_core import TaskManagerCore, create_prompts
from pathlib import Path

core = TaskManagerCore(Path('$INSTALL_DIR'))
create_prompts(Path('$INSTALL_DIR'))
print('✅ Database initialized')
"

# Check for existing installations to migrate
echo -e "\n🔍 Checking for existing QTM installations..."
if [[ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs/toolbox/qwen_task_manager" ]]; then
    echo "Found QTM v1 installation"
    read -p "Migrate existing tasks and reflections? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$SCRIPT_DIR/migrate_to_v3.py" "$INSTALL_DIR/"
        python3 "$INSTALL_DIR/migrate_to_v3.py"
    fi
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo -e "\n📝 Adding to PATH..."
    
    # Detect shell
    if [[ -n "$ZSH_VERSION" ]]; then
        SHELL_RC="$HOME/.zshrc"
    elif [[ -n "$BASH_VERSION" ]]; then
        SHELL_RC="$HOME/.bashrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    echo "" >> "$SHELL_RC"
    echo "# Qwen Task Manager 3.0" >> "$SHELL_RC"
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
    
    echo "✅ Added to $SHELL_RC"
fi

# Create helpful aliases
echo -e "\n🎯 Creating helpful aliases..."
cat > "$INSTALL_DIR/aliases.sh" << 'EOF'
# Qwen Task Manager 3.0 Aliases
alias qt='qtm3'
alias qta='qtm3 add'
alias qtt='qtm3 today'
alias qtr='qtm3 reflect'

# Quick brain dump
qbrain() {
    echo "$*" | qtm3 add
}

# Project-specific task add
qtproject() {
    local project=$1
    shift
    echo "[$project] $*" | qtm3 add
}
EOF

echo "To use aliases, add this to your shell config:"
echo "  source $INSTALL_DIR/aliases.sh"

# Success!
echo -e "\n✨ Installation complete!"
echo "========================================"
echo "🚀 Quick start:"
echo "   qtm3          - Launch task manager"
echo "   qtm3 add      - Quick add task"
echo "   qtm3 today    - View today's tasks"
echo "   qtm3 reflect  - Daily reflection"
echo ""
echo "📚 Documentation: $INSTALL_DIR/README.md"
echo ""
echo "💡 First time? Try:"
echo "   1. qtm3 → Brain Dump"
echo "   2. qtm3 → Prioritize"
echo "   3. qtm3 → Reflect (evening)"
echo ""
echo "Restart your shell or run: source ~/.zshrc"