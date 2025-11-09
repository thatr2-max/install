"""System prompt builder for the AI modding agent."""

import json
from typing import Dict, Any
from pathlib import Path


def _get_prompts_dir() -> Path:
    """Get the prompts directory path."""
    # Assuming this file is in src/agent/, go up to project root
    return Path(__file__).parent.parent.parent / "prompts"


def load_prompt_template(template_name: str = "system_prompt.txt") -> str:
    """Load a prompt template from file.

    Args:
        template_name: Name of the template file

    Returns:
        Template content as string
    """
    prompts_dir = _get_prompts_dir()
    template_path = prompts_dir / template_name

    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to default if file doesn't exist
        return _get_default_system_prompt()


def _get_default_system_prompt() -> str:
    """Fallback default system prompt if file not found."""
    return """You are an expert {game} modder with access to powerful tools.

YOUR WORKFLOW:
1. Research using tools (3-6 tool calls max)
2. Plan the mod (save_draft with name "plan")
3. Generate mod files
4. Validate using validate_json
5. Output files with format: --- FILE: path/to/file.ext ---

CRITICAL: Don't get stuck researching. After 6 tool calls, START GENERATING.

FILE OUTPUT FORMAT:
--- FILE: path/to/file.json ---
{{"content": "here"}}
"""


def build_system_prompt(game: str, additional_context: str = "") -> str:
    """Build system prompt for the AI agent.

    Args:
        game: Game identifier (e.g., "cdda")
        additional_context: Additional game-specific context

    Returns:
        Complete system prompt
    """
    template = load_prompt_template("system_prompt.txt")
    prompt = template.format(game=game.upper())

    if additional_context:
        prompt += f"\n\nGAME-SPECIFIC NOTES:\n{additional_context}"

    return prompt


def build_refinement_prompt(game: str, current_files: Dict[str, str], feedback: str) -> str:
    """Build prompt for refining an existing mod.

    Args:
        game: Game identifier
        current_files: Dictionary of current mod files
        feedback: User feedback for refinement

    Returns:
        Refinement prompt
    """
    template = load_prompt_template("refinement_prompt.txt")

    # Format current files nicely
    files_display = "\n".join([
        f"--- FILE: {path} ---\n{content[:200]}{'...' if len(content) > 200 else ''}\n"
        for path, content in current_files.items()
    ])

    game_notes = get_game_specific_notes(game)

    prompt = template.format(
        game=game.upper(),
        current_files=files_display,
        feedback=feedback
    )

    if game_notes:
        prompt += f"\n\nGAME-SPECIFIC NOTES:\n{game_notes}"

    return prompt


def get_game_specific_notes(game: str) -> str:
    """Get game-specific modding notes from file.

    Args:
        game: Game identifier

    Returns:
        Game-specific notes to include in system prompt
    """
    prompts_dir = _get_prompts_dir()
    notes_path = prompts_dir / "game_notes.json"

    if notes_path.exists():
        with open(notes_path, 'r', encoding='utf-8') as f:
            all_notes = json.load(f)
            game_data = all_notes.get(game, {})
            notes_list = game_data.get("notes", [])
            if notes_list:
                return "\n".join(f"- {note}" for note in notes_list)

    # Fallback to empty if not found
    return ""
