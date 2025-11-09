# Prompt Customization

This directory contains all the prompts used by the AI Mod Generator. You can edit these files to customize how the AI behaves!

## Files

### `system_prompt.txt`
The main system prompt used when creating new mods. This defines the AI's workflow, rules, and philosophy.

**Edit this to:**
- Change the research → plan → generate → validate workflow
- Adjust how many tool calls the AI should make before generating
- Modify the AI's personality or approach
- Add custom rules or guidelines

**Format placeholders:**
- `{game}` - Will be replaced with the game name (e.g., "CDDA")

**Example customizations:**
- Make the AI more conservative: "Never exceed 4 tool calls during research"
- Make it faster: "Skip planning phase for simple mods"
- Add strictness: "ALWAYS use validate_json before finalizing"

### `refinement_prompt.txt`
Used when refining existing mods with the `refine` command.

**Edit this to:**
- Change how the AI approaches feedback
- Adjust preservation vs. recreation balance
- Add specific refinement rules

**Format placeholders:**
- `{game}` - Game name
- `{current_files}` - Current mod files (auto-populated)
- `{feedback}` - User's feedback (auto-populated)

### `game_notes.json`
Game-specific modding guidelines and rules.

**Edit this to:**
- Add new games
- Update file format requirements
- Add game-specific gotchas
- Include balance guidelines

**Structure:**
```json
{
  "game_name": {
    "notes": [
      "Note 1",
      "Note 2"
    ]
  }
}
```

## How to Customize

### 1. Quick Edits
Just open the file and edit! Changes take effect immediately on the next run.

```bash
# Edit the main system prompt
nano prompts/system_prompt.txt

# Then test
python cli.py create cdda "test mod"
```

### 2. Add a New Game
Edit `game_notes.json`:

```json
{
  "my_game": {
    "notes": [
      "Uses YAML format",
      "IDs must be unique",
      "Special characters forbidden"
    ]
  }
}
```

### 3. Create Custom Variants
You can create multiple prompt files and load them programmatically:

```python
# In your code
from src.agent.system_prompt import load_prompt_template

custom_prompt = load_prompt_template("my_custom_prompt.txt")
```

## Tips for Prompt Engineering

### Be Specific
❌ "Make good mods"
✅ "Mods must have balanced stats, unique IDs, and installation instructions"

### Use Examples
```
BAD EXAMPLE:
{"id": "op_sword", "damage": 9999}

GOOD EXAMPLE:
{"id": "steel_longsword", "damage": 38}
```

### Set Limits
```
Research Phase: Maximum 6 tool calls
Planning Phase: 3-5 lines for simple, 10-20 for complex
Validation: ALWAYS run validate_json
```

### Add Constraints
```
NEVER:
- Generate IDs with spaces
- Skip validation
- Use placeholder values like "TODO" or "FIX_ME"

ALWAYS:
- Include comments explaining complex logic
- Test against schema
- Provide installation instructions
```

## Testing Prompts

After editing prompts, test with increasing complexity:

```bash
# 1. Simple test
python cli.py create cdda "add a knife" --verbose

# 2. Medium test
python cli.py create cdda "new weapon category"

# 3. Complex test
python cli.py create cdda "complete crafting system for brewing"
```

Watch the logs to see how the AI responds to your changes:
```bash
tail -f logs/agent_decisions.log
```

## Common Customizations

### Make AI Faster (Less Research)
```diff
- Research should take 3-6 tool calls maximum
+ Research should take 1-3 tool calls maximum
```

### Make AI More Thorough
```diff
- After research + planning, you MUST move to generation
+ After research + planning + validation simulation, THEN generate
```

### Change Iteration Limits
```diff
- If you've made more than 8 tool calls and haven't started outputting
+ If you've made more than 15 tool calls and haven't started outputting
```

### Add Custom Validation
```
MANDATORY VALIDATION STEPS:
1. validate_json - Check syntax
2. validate_references - Check all IDs exist
3. validate_balance - Compare to vanilla
4. validate_lore - Check naming conventions
```

## Fallback Behavior

If a prompt file is missing, the system uses a minimal hardcoded fallback. See `src/agent/system_prompt.py` for the default.

## Sharing Prompts

Found a great prompt configuration? Share it!

1. Save your custom prompts
2. Test thoroughly
3. Share in the community with your results

## Questions?

- Check `src/agent/system_prompt.py` to see how prompts are loaded
- Read the main README.md for usage examples
- Experiment! The AI is resilient to prompt changes
