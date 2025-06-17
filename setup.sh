#!/usr/bin/env zsh

# Quick Setup Script for Qwen Task Manager

echo "🚀 Setting up Qwen Task Manager..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install it first:"
    echo "   brew install ollama"
    exit 1
fi

# Check if Qwen model exists
if ! ollama list | grep -q "qwen3:30b-a3b"; then
    echo "📥 Pulling Qwen model (this may take a while)..."
    ollama pull qwen3:30b-a3b
fi

# Make main script executable
chmod +x run_task_manager.zsh

# Create archive directory
mkdir -p tasks/archive

# Create initial example task
echo "- [ ] Try out the Qwen task manager
- [ ] Read the README for usage tips
- [ ] Set up daily reflection habit" > tasks/backlog.txt

echo "✅ Setup complete!"
echo ""
echo "To start using the task manager:"
echo "   ./run_task_manager.zsh"
echo ""
echo "For quick access, add this alias to your ~/.zshrc:"
echo "   alias tasks='$(pwd)/run_task_manager.zsh'"