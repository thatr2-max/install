# AI Mod Generator

An AI-powered mod creation system that uses agentic workflows and tool calling to generate high-quality game mods.

## Overview

This isn't just a prompt-and-pray generator. This is a **real AI agent** that:
- 📚 Researches before generating (reads examples, docs, schemas)
- 🎯 Plans based on self-assessed complexity
- ✅ Validates its own work
- 🔄 Iterates until the mod is actually good
- 🛠️ Uses tools like a human modder would

## Features

- **Agentic Architecture**: Uses OpenRouter API with Qwen3-Next-80B-A3B-Instruct model
- **Tool-Based Workflow**: AI can research examples, read docs, validate output
- **Self-Assessed Planning**: AI determines complexity and creates appropriate plans
- **Multi-Game Support**: CDDA, RimWorld, Factorio, and more
- **Cost Tracking**: Detailed token usage and cost monitoring
- **Validation**: Syntax checking, reference validation, balance analysis

## Installation

### Prerequisites

- Python 3.8+
- OpenRouter API key ([get one here](https://openrouter.ai/))

### Setup

1. Clone the repository:
```bash
cd ai-mod-generator
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API key:
Edit `config.json` and replace `PLACEHOLDER` with your OpenRouter API key:
```json
{
  "openrouter_api_key": "sk-or-v1-your-actual-key-here",
  ...
}
```

## Quick Start

### 1. Learn from Examples

First, the AI needs to learn modding patterns for your game:

1. Create example directory:
```bash
mkdir -p game_schemas/cdda/examples
```

2. Add 5-10 example mods (each in its own subdirectory)

3. Optionally add documentation:
```bash
mkdir -p game_schemas/cdda/docs
# Add .md or .pdf modding documentation
```

4. Run learning:
```bash
python cli.py learn cdda
```

### 2. Generate a Mod

```bash
python cli.py create cdda "A flamethrower that uses cooking oil as fuel"
```

The AI will:
1. Research similar examples
2. Plan the implementation
3. Generate mod files
4. Validate the output
5. Save to `output/cdda/[mod_name]/`

### 3. Check Costs

```bash
python cli.py cost
```

## Commands

### `learn [game]`
Learn modding patterns from example mods.

```bash
python cli.py learn cdda
```

### `create [game] "[description]"`
Generate a new mod using AI agent.

```bash
python cli.py create cdda "Add a laser rifle weapon"
```

Options:
- `--verbose`: Show detailed agent reasoning
- `--max-iterations N`: Override max iteration limit (default: 10)
- `--output-dir PATH`: Custom output directory

### `list`
List all learned games and their details.

```bash
python cli.py list
```

### `cost`
Show total API usage and cost.

```bash
python cli.py cost
```

## Supported Games

- **CDDA** (Cataclysm: Dark Days Ahead) - JSON format
- **RimWorld** - XML format
- **Factorio** - Lua format
- **Project Zomboid** - Lua format
- **Terraria** - JSON format
- **Stardew Valley** - JSON format

## How It Works

### Agentic Workflow

1. **Research Phase**
   - AI uses tools to find similar examples
   - Reads documentation about relevant mechanics
   - Studies schema patterns

2. **Planning Phase**
   - AI self-assesses complexity
   - Creates appropriate plan (3 lines for simple, detailed for complex)
   - Saves plan for reference

3. **Generation Phase**
   - Creates mod files following plan
   - Uses learned patterns
   - Maintains consistency

4. **Validation Phase**
   - Validates JSON/XML syntax
   - Checks references
   - Reviews balance

5. **Refinement Phase** (if needed)
   - Fixes validation errors
   - Adjusts based on warnings
   - Iterates until clean

### Available Tools

The AI has access to these tools:
- `view_schema_file`: Read learned patterns
- `list_template_types`: See available templates
- `get_template`: Get complete template structure
- `list_examples`: Browse example mods
- `read_example_mod`: Study specific examples
- `save_draft`: Save work-in-progress (plans, drafts)
- `load_draft`: Load saved drafts
- `validate_json`: Check JSON syntax
- `search_documentation`: Search modding docs

## Cost Economics

Using Qwen3-Next-80B-A3B-Instruct:
- Input: $0.15 per 1M tokens
- Output: $1.50 per 1M tokens

**Typical costs:**
- Simple mod (value tweak): ~$0.001
- Medium mod (new item): ~$0.005
- Complex mod (new system): ~$0.012

With a $250 budget, you can generate **100-200+ excellent mods**.

## Directory Structure

```
ai-mod-generator/
├── game_schemas/          # Learned patterns for each game
│   ├── cdda/
│   │   ├── schema.json           # Extracted structure/patterns
│   │   ├── examples/             # Your example mods
│   │   └── docs/                 # Modding documentation
│   └── rimworld/
├── output/                # Generated mods
├── plans/                 # Saved planning phases
├── logs/                  # Agent logs and cost tracking
├── src/
│   ├── agent/            # Agentic orchestration
│   ├── learner/          # Schema learning
│   ├── validation/       # Validation systems
│   └── utils/
├── cli.py                # Command-line interface
└── config.json           # Configuration
```

## Configuration

Edit `config.json` to customize:

```json
{
  "openrouter_api_key": "your-key-here",
  "model": "qwen/qwen3-next-80b-a3b-instruct",
  "max_iterations": 10,
  "enable_tool_use": true,
  "log_level": "INFO",
  "cost_tracking": {
    "input_cost_per_1m_tokens": 0.15,
    "output_cost_per_1m_tokens": 1.50,
    "warn_threshold_usd": 1.00
  }
}
```

## Examples

### Simple Mod
```bash
python cli.py create cdda "Increase zombie spawn rate by 50%"
```
Result: Quick config file modification

### Medium Mod
```bash
python cli.py create cdda "A new katana weapon with balanced stats"
```
Result: Item definition with proper balance

### Complex Mod
```bash
python cli.py create cdda "A complete crafting system for brewing beer"
```
Result: Multiple files with items, recipes, and mechanics

## Troubleshooting

### "No schema found for [game]"
Run `python cli.py learn [game]` first to analyze example mods.

### "API key not configured"
Edit `config.json` and add your OpenRouter API key.

### "No examples found"
Add example mods to `game_schemas/[game]/examples/` before learning.

### High costs
- Reduce `max_iterations` in config
- Start with simpler mods
- Use `--verbose` to see what the AI is doing

## Logs

All operations are logged to `logs/`:
- `api_usage.log`: API calls and token usage
- `tool_usage.log`: Tool executions
- `agent_decisions.log`: High-level workflow decisions
- `cost_tracker.json`: Cumulative cost tracking

## Contributing

To add support for a new game:
1. Create directory in `game_schemas/[game]/`
2. Add example mods to `examples/`
3. Add documentation to `docs/`
4. Run learning: `python cli.py learn [game]`
5. Test generation with various complexities

## License

MIT License - see LICENSE file for details

## Credits

Created using Claude Code and inspired by the agentic AI architecture philosophy.

Powered by OpenRouter and Qwen3-Next-80B-A3B-Instruct.
