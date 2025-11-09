"""Main agentic orchestrator for mod generation."""

import json
import logging
import re
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from ..openrouter_client import OpenRouterClient
from .tool_executor import ToolExecutor
from .system_prompt import build_system_prompt, build_refinement_prompt, get_game_specific_notes

logger = logging.getLogger(__name__)


class ModdingAgent:
    """AI agent that creates mods using tools and iteration."""

    def __init__(self, client: OpenRouterClient, project_root: Path, log_dir: Path):
        """Initialize modding agent.

        Args:
            client: OpenRouter API client
            project_root: Root directory of the project
            log_dir: Directory for logs
        """
        self.client = client
        self.project_root = Path(project_root)
        self.log_dir = Path(log_dir)
        self.tool_executor = ToolExecutor(project_root, log_dir)

        # Agent decision log
        self.decision_log = self.log_dir / "agent_decisions.log"

    def generate_mod(
        self,
        game: str,
        description: str,
        max_iterations: int = 10,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Generate a mod using agentic workflow.

        Args:
            game: Game identifier
            description: Natural language description of the mod
            max_iterations: Maximum number of iterations
            verbose: Whether to log verbose output

        Returns:
            Dictionary containing generation results
        """
        logger.info(f"Starting mod generation for {game}: {description}")
        self._log_decision(f"Starting generation: {description}")

        # Build system prompt
        game_notes = get_game_specific_notes(game)
        system_prompt = build_system_prompt(game, game_notes)

        # Initialize conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create this mod: {description}"}
        ]

        iteration = 0
        tool_call_log = []

        try:
            while iteration < max_iterations:
                iteration += 1
                self._log_decision(f"Iteration {iteration}/{max_iterations}")

                if verbose:
                    logger.info(f"Iteration {iteration}/{max_iterations}")

                # Call AI with tools
                response = self.client.chat(
                    messages=messages,
                    tools=self.tool_executor.get_tool_definitions(),
                    temperature=0.7,
                    max_tokens=4000
                )

                # Check if AI wants to use tools
                if response.has_tool_calls():
                    tool_names = [tc.name for tc in response.tool_calls]
                    self._log_decision(f"AI requested {len(response.tool_calls)} tool calls: {', '.join(tool_names)}")

                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [tc.to_dict() for tc in response.tool_calls]
                    })

                    # Execute each tool call
                    for tool_call in response.tool_calls:
                        if verbose:
                            logger.info(f"Executing tool: {tool_call.name}")

                        # Execute tool
                        result = self.tool_executor.execute_tool(
                            tool_call.name,
                            tool_call.arguments
                        )

                        # Log tool call with result summary
                        success = result.get("success", False)
                        status = "✓" if success else "✗"
                        result_summary = ""
                        if success and result.get("data"):
                            data = result["data"]
                            if isinstance(data, dict):
                                result_summary = f" -> {len(data)} items" if data else " -> empty"
                            elif isinstance(data, list):
                                result_summary = f" -> {len(data)} results"
                        elif not success:
                            result_summary = f" -> Error: {result.get('error', 'unknown')}"

                        self._log_decision(f"  {status} {tool_call.name}{result_summary}")

                        tool_call_log.append({
                            "iteration": iteration,
                            "tool": tool_call.name,
                            "arguments": tool_call.arguments,
                            "success": success
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })

                    continue

                # AI has final answer
                if response.is_final():
                    self._log_decision("AI provided final output")
                    return self._parse_final_output(
                        response.content,
                        tool_call_log,
                        game,
                        description,
                        iteration
                    )

                # If neither tool calls nor final content, something went wrong
                logger.warning("Response has neither tool calls nor final content")
                iteration += 1

            # Max iterations exceeded - make one final attempt to get output
            self._log_decision(f"Max iterations ({max_iterations}) reached - requesting final output")
            logger.warning(f"Max iterations reached, forcing final output")

            # Add a strong prompt to generate NOW
            messages.append({
                "role": "user",
                "content": (
                    "You have reached the maximum iteration limit. Please provide your final mod output NOW. "
                    "Output all files using the format:\n"
                    "--- FILE: path/to/file.ext ---\n"
                    "file content\n\n"
                    "Even if the mod is incomplete, provide what you have created so far. "
                    "Do NOT call any more tools - just output the files."
                )
            })

            # Make final call without tools to force text output
            final_response = self.client.chat(
                messages=messages,
                tools=None,  # No tools available - must respond with text
                temperature=0.7,
                max_tokens=4000
            )

            self._log_decision("Received forced final output")

            if final_response.content:
                return self._parse_final_output(
                    final_response.content,
                    tool_call_log,
                    game,
                    description,
                    max_iterations + 1
                )
            else:
                # Still no output - return error with tool history
                self._log_decision("No output even after forcing - returning error")
                return {
                    "success": False,
                    "error": (
                        f"Agent exhausted max iterations ({max_iterations}) and did not produce output. "
                        f"The agent made {len(tool_call_log)} tool calls but never moved to generation phase. "
                        "Try: (1) Increasing max_iterations, (2) Simplifying the request, or "
                        "(3) Checking if the schema/examples are properly set up."
                    ),
                    "tool_calls": tool_call_log,
                    "iterations": max_iterations,
                    "hint": "Agent may be stuck in research phase. Check logs to see what tools it's repeatedly calling."
                }

        except Exception as e:
            logger.error(f"Error during generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_calls": tool_call_log,
                "iterations": iteration
            }

    def refine_mod(
        self,
        game: str,
        mod_path: Path,
        feedback: str,
        max_iterations: int = 10,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Refine an existing mod based on user feedback.

        Args:
            game: Game identifier
            mod_path: Path to the mod directory to refine
            feedback: User feedback describing desired changes
            max_iterations: Maximum number of iterations
            verbose: Whether to log verbose output

        Returns:
            Dictionary containing refinement results
        """
        logger.info(f"Starting mod refinement for {mod_path}")
        self._log_decision(f"Starting refinement: {feedback}")

        # Load existing mod files
        mod_path = Path(mod_path)
        if not mod_path.exists():
            return {
                "success": False,
                "error": f"Mod directory not found: {mod_path}"
            }

        current_files = self._load_mod_files(mod_path)
        if not current_files:
            return {
                "success": False,
                "error": f"No mod files found in {mod_path}"
            }

        self._log_decision(f"Loaded {len(current_files)} files from existing mod")

        # Build refinement prompt
        system_prompt = build_refinement_prompt(game, current_files, feedback)

        # Initialize conversation
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please refine the mod based on this feedback: {feedback}"}
        ]

        iteration = 0
        tool_call_log = []

        try:
            while iteration < max_iterations:
                iteration += 1
                self._log_decision(f"Refinement iteration {iteration}/{max_iterations}")

                if verbose:
                    logger.info(f"Iteration {iteration}/{max_iterations}")

                # Call AI with tools
                response = self.client.chat(
                    messages=messages,
                    tools=self.tool_executor.get_tool_definitions(),
                    temperature=0.7,
                    max_tokens=4000
                )

                # Check if AI wants to use tools
                if response.has_tool_calls():
                    tool_names = [tc.name for tc in response.tool_calls]
                    self._log_decision(f"AI requested {len(response.tool_calls)} tool calls: {', '.join(tool_names)}")

                    # Add assistant message with tool calls
                    messages.append({
                        "role": "assistant",
                        "content": response.content,
                        "tool_calls": [tc.to_dict() for tc in response.tool_calls]
                    })

                    # Execute each tool call
                    for tool_call in response.tool_calls:
                        if verbose:
                            logger.info(f"Executing tool: {tool_call.name}")

                        # Execute tool
                        result = self.tool_executor.execute_tool(
                            tool_call.name,
                            tool_call.arguments
                        )

                        # Log tool call with result summary
                        success = result.get("success", False)
                        status = "✓" if success else "✗"
                        result_summary = ""
                        if success and result.get("data"):
                            data = result["data"]
                            if isinstance(data, dict):
                                result_summary = f" -> {len(data)} items" if data else " -> empty"
                            elif isinstance(data, list):
                                result_summary = f" -> {len(data)} results"
                        elif not success:
                            result_summary = f" -> Error: {result.get('error', 'unknown')}"

                        self._log_decision(f"  {status} {tool_call.name}{result_summary}")

                        tool_call_log.append({
                            "iteration": iteration,
                            "tool": tool_call.name,
                            "arguments": tool_call.arguments,
                            "success": success
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })

                    continue

                # AI has final answer
                if response.is_final():
                    self._log_decision("AI provided refined output")
                    return self._parse_final_output(
                        response.content,
                        tool_call_log,
                        game,
                        f"Refinement: {feedback}",
                        iteration
                    )

                # If neither tool calls nor final content, something went wrong
                logger.warning("Response has neither tool calls nor final content")
                iteration += 1

            # Max iterations exceeded - force output
            self._log_decision(f"Max iterations ({max_iterations}) reached - requesting final output")

            messages.append({
                "role": "user",
                "content": (
                    "You have reached the maximum iteration limit. Please provide your refined mod output NOW. "
                    "Output all files using the format:\n"
                    "--- FILE: path/to/file.ext ---\n"
                    "file content\n\n"
                    "Even if incomplete, provide what you have."
                )
            })

            final_response = self.client.chat(
                messages=messages,
                tools=None,
                temperature=0.7,
                max_tokens=4000
            )

            if final_response.content:
                return self._parse_final_output(
                    final_response.content,
                    tool_call_log,
                    game,
                    f"Refinement: {feedback}",
                    max_iterations + 1
                )
            else:
                return {
                    "success": False,
                    "error": f"Refinement exhausted max iterations ({max_iterations}) without output.",
                    "tool_calls": tool_call_log,
                    "iterations": max_iterations
                }

        except Exception as e:
            logger.error(f"Error during refinement: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_calls": tool_call_log,
                "iterations": iteration
            }

    def _load_mod_files(self, mod_path: Path) -> Dict[str, str]:
        """Load all files from a mod directory.

        Args:
            mod_path: Path to mod directory

        Returns:
            Dictionary mapping file paths to content
        """
        files = {}
        for file_path in mod_path.rglob("*"):
            if file_path.is_file():
                # Skip binary files and common non-mod files
                if file_path.suffix in ['.json', '.xml', '.lua', '.txt', '.md']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            rel_path = str(file_path.relative_to(mod_path))
                            files[rel_path] = content
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")
        return files

    def _parse_final_output(
        self,
        content: str,
        tool_call_log: List[Dict[str, Any]],
        game: str,
        description: str,
        iterations: int
    ) -> Dict[str, Any]:
        """Parse final output from AI.

        Args:
            content: AI's final response content
            tool_call_log: Log of all tool calls made
            game: Game identifier
            description: Original mod description
            iterations: Number of iterations used

        Returns:
            Parsed output with files and metadata
        """
        logger.info("Parsing final output")

        # Extract files using delimiter format
        files = self._extract_files(content)

        if not files:
            logger.warning("No files found in output")
            return {
                "success": False,
                "error": "No mod files were generated",
                "raw_output": content,
                "tool_calls": tool_call_log,
                "iterations": iterations
            }

        # Extract plan from drafts (if saved)
        plan = None
        for log_entry in tool_call_log:
            if log_entry["tool"] == "save_draft" and log_entry["arguments"].get("draft_name") == "plan":
                plan = log_entry["arguments"].get("content")
                break

        # Determine mod name from files or description
        mod_name = self._determine_mod_name(files, description)

        result = {
            "success": True,
            "mod_name": mod_name,
            "files": files,
            "plan": plan,
            "metadata": {
                "game": game,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "iterations": iterations,
                "tool_calls_count": len(tool_call_log),
                "tool_calls": tool_call_log
            },
            "warnings": self._check_for_warnings(files)
        }

        logger.info(f"Successfully generated mod with {len(files)} files")
        return result

    def _extract_files(self, content: str) -> Dict[str, str]:
        """Extract files from AI output using delimiter format.

        Expected format:
        --- FILE: path/to/file.ext ---
        file content here
        --- FILE: another/file.ext ---
        more content

        Args:
            content: AI output content

        Returns:
            Dictionary mapping file paths to content
        """
        files = {}
        pattern = r'---\s*FILE:\s*([^\n]+)\s*---\s*\n(.*?)(?=---\s*FILE:|$)'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            file_path = match.group(1).strip()
            file_content = match.group(2).strip()

            # Clean up markdown code blocks if present
            file_content = re.sub(r'^```\w*\n', '', file_content)
            file_content = re.sub(r'\n```$', '', file_content)

            files[file_path] = file_content

        return files

    def _determine_mod_name(self, files: Dict[str, str], description: str) -> str:
        """Determine mod name from files or description.

        Args:
            files: Generated files
            description: Mod description

        Returns:
            Mod name
        """
        # Try to find mod name from modinfo.json or similar
        for path, content in files.items():
            if 'modinfo' in path.lower() or 'about' in path.lower():
                try:
                    data = json.loads(content)
                    if 'name' in data:
                        return data['name']
                    if 'id' in data:
                        return data['id']
                except:
                    pass

        # Generate from description
        # Take first few words, clean up, make safe filename
        words = description.lower().split()[:4]
        name = '_'.join(w for w in words if w.isalnum())
        return name or "generated_mod"

    def _check_for_warnings(self, files: Dict[str, str]) -> List[str]:
        """Check for potential warnings in generated files.

        Args:
            files: Generated files

        Returns:
            List of warning messages
        """
        warnings = []

        # Check if README exists
        if not any('readme' in path.lower() for path in files.keys()):
            warnings.append("No README file generated - users may not know how to install")

        # Check for empty files
        for path, content in files.items():
            if not content.strip():
                warnings.append(f"File appears empty: {path}")

        # Check JSON syntax
        for path, content in files.items():
            if path.endswith('.json'):
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    warnings.append(f"JSON syntax error in {path}: {e}")

        return warnings

    def _log_decision(self, message: str):
        """Log agent decision to file.

        Args:
            message: Decision message
        """
        log_entry = f"{datetime.now().isoformat()} | {message}\n"
        with open(self.decision_log, 'a') as f:
            f.write(log_entry)
