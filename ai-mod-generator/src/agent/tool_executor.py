"""Tool execution engine for AI agent."""

import json
import logging
from typing import Dict, Any, List, Callable
from pathlib import Path
from datetime import datetime

from .tools import ModdingTools

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Manages tool registry and executes tool calls from AI."""

    def __init__(self, project_root: Path, log_dir: Path):
        """Initialize tool executor.

        Args:
            project_root: Root directory of the project
            log_dir: Directory for tool usage logs
        """
        self.project_root = Path(project_root)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.tool_log = self.log_dir / "tool_usage.log"

        # Initialize tools
        self.tools = ModdingTools(project_root)

        # Register tool functions
        self.tool_registry: Dict[str, Callable] = {
            "view_schema_file": self.tools.view_schema_file,
            "list_template_types": self.tools.list_template_types,
            "get_template": self.tools.get_template,
            "list_examples": self.tools.list_examples,
            "read_example_mod": self.tools.read_example_mod,
            "save_draft": self.tools.save_draft,
            "load_draft": self.tools.load_draft,
            "validate_json": self.tools.validate_json,
            "search_documentation": self.tools.search_documentation,
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions in OpenAI function calling format.

        Returns:
            List of tool definitions
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "view_schema_file",
                    "description": "Read a specific section of the learned game schema to understand mod structure and patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier (e.g., 'cdda', 'rimworld')"
                            },
                            "section": {
                                "type": "string",
                                "description": "Schema section to read (e.g., 'templates', 'mod_structure')"
                            }
                        },
                        "required": ["game", "section"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_template_types",
                    "description": "List all available mod templates for a game (e.g., items, recipes, professions)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            }
                        },
                        "required": ["game"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_template",
                    "description": "Get complete template structure with all fields, examples, and patterns for a specific mod type",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            },
                            "template_type": {
                                "type": "string",
                                "description": "Type of template to get (e.g., 'item', 'recipe')"
                            }
                        },
                        "required": ["game", "template_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_examples",
                    "description": "Browse available example mods to see what reference implementations exist",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            },
                            "filter_type": {
                                "type": "string",
                                "description": "Optional filter by mod type"
                            }
                        },
                        "required": ["game"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_example_mod",
                    "description": "Deep read a specific example mod to understand implementation patterns and best practices",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            },
                            "example_name": {
                                "type": "string",
                                "description": "Name of the example mod to read"
                            }
                        },
                        "required": ["game", "example_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_draft",
                    "description": "Save work-in-progress content like plans or draft mods for later reference",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            },
                            "draft_name": {
                                "type": "string",
                                "description": "Name for the draft (e.g., 'plan', 'v1')"
                            },
                            "content": {
                                "type": ["object", "array", "string"],
                                "description": "Content to save"
                            }
                        },
                        "required": ["game", "draft_name", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "load_draft",
                    "description": "Load previously saved draft content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            },
                            "draft_name": {
                                "type": "string",
                                "description": "Name of the draft to load"
                            }
                        },
                        "required": ["game", "draft_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "validate_json",
                    "description": "Check if JSON content is syntactically valid",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "JSON string to validate"
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_documentation",
                    "description": "Search game's modding documentation for specific information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "game": {
                                "type": "string",
                                "description": "Game identifier"
                            },
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            }
                        },
                        "required": ["game", "query"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        try:
            # Log tool call
            self._log_tool_call(tool_name, arguments)

            # Check if tool exists
            if tool_name not in self.tool_registry:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "data": None
                }

            # Execute tool
            tool_func = self.tool_registry[tool_name]
            result = tool_func(**arguments)

            # Log result
            self._log_tool_result(tool_name, result)

            return result

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Tool execution error: {str(e)}",
                "data": None
            }

    def _log_tool_call(self, tool_name: str, arguments: Dict[str, Any]):
        """Log tool call to file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": arguments
        }
        with open(self.tool_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _log_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """Log tool result to file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "success": result.get("success", False),
            "has_data": result.get("data") is not None
        }
        with open(self.tool_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
