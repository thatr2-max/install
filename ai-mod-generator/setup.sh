#!/bin/bash
# Setup script for AI Mod Generator

echo "🚀 Setting up AI Mod Generator..."
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p output
mkdir -p plans
mkdir -p game_schemas/cdda/{examples,docs,vanilla_data}
mkdir -p game_schemas/rimworld/{examples,docs,vanilla_data}
mkdir -p game_schemas/factorio/{examples,docs,vanilla_data}

echo
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "1. Edit config.json and add your OpenRouter API key"
echo "2. Add example mods to game_schemas/[game]/examples/"
echo "3. Run: python cli.py learn [game]"
echo "4. Run: python cli.py create [game] \"[description]\""
echo
echo "For help: python cli.py --help"
echo
