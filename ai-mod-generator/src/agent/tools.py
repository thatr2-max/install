"""Tool implementations for the AI agent."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ModdingTools:
    """Collection of tools available to the AI agent."""

    def __init__(self, project_root: Path):
        """Initialize tools with project root directory.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.schemas_dir = self.project_root / "game_schemas"
        self.drafts = {}  # In-memory draft storage

    def view_schema_file(self, game: str, section: str) -> Dict[str, Any]:
        """Read a specific section of the learned game schema.

        Args:
            game: Game identifier (e.g., "cdda")
            section: Schema section to read (e.g., "templates", "mod_structure")

        Returns:
            Dictionary containing the requested schema section
        """
        try:
            schema_path = self.schemas_dir / game / "schema.json"
            if not schema_path.exists():
                return {
                    "success": False,
                    "error": f"Schema not found for game: {game}",
                    "data": None
                }

            with open(schema_path, 'r') as f:
                schema = json.load(f)

            if section not in schema:
                return {
                    "success": False,
                    "error": f"Section '{section}' not found in schema",
                    "data": None,
                    "metadata": {"available_sections": list(schema.keys())}
                }

            return {
                "success": True,
                "data": schema[section],
                "error": None,
                "metadata": {"game": game, "section": section}
            }

        except Exception as e:
            logger.error(f"Error reading schema: {e}")
            return {"success": False, "error": str(e), "data": None}

    def list_template_types(self, game: str) -> Dict[str, Any]:
        """List all available templates for a game.

        Args:
            game: Game identifier

        Returns:
            List of template names with brief descriptions
        """
        try:
            schema_result = self.view_schema_file(game, "templates")
            if not schema_result["success"]:
                return schema_result

            templates = schema_result["data"]
            template_list = []
            for name, details in templates.items():
                template_list.append({
                    "name": name,
                    "required_fields_count": len(details.get("required_fields", [])),
                    "optional_fields_count": len(details.get("optional_fields", [])),
                    "has_examples": len(details.get("examples", [])) > 0
                })

            return {
                "success": True,
                "data": template_list,
                "error": None,
                "metadata": {"game": game, "count": len(template_list)}
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def get_template(self, game: str, template_type: str) -> Dict[str, Any]:
        """Get full template with all fields and examples.

        Args:
            game: Game identifier
            template_type: Type of template (e.g., "item", "recipe")

        Returns:
            Complete template structure
        """
        try:
            schema_result = self.view_schema_file(game, "templates")
            if not schema_result["success"]:
                return schema_result

            templates = schema_result["data"]
            if template_type not in templates:
                return {
                    "success": False,
                    "error": f"Template type '{template_type}' not found",
                    "data": None,
                    "metadata": {"available_templates": list(templates.keys())}
                }

            return {
                "success": True,
                "data": templates[template_type],
                "error": None,
                "metadata": {"game": game, "template_type": template_type}
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def list_examples(self, game: str, filter_type: Optional[str] = None) -> Dict[str, Any]:
        """Browse available example mods.

        Args:
            game: Game identifier
            filter_type: Optional filter by mod type

        Returns:
            List of example mod names and descriptions
        """
        try:
            examples_dir = self.schemas_dir / game / "examples"
            if not examples_dir.exists():
                return {
                    "success": False,
                    "error": f"Examples directory not found for game: {game}",
                    "data": None
                }

            examples = []
            for mod_dir in examples_dir.iterdir():
                if mod_dir.is_dir():
                    examples.append({
                        "name": mod_dir.name,
                        "path": str(mod_dir.relative_to(self.project_root)),
                        "files": [f.name for f in mod_dir.iterdir() if f.is_file()]
                    })

            return {
                "success": True,
                "data": examples,
                "error": None,
                "metadata": {"game": game, "count": len(examples)}
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def read_example_mod(self, game: str, example_name: str) -> Dict[str, Any]:
        """Read a specific example mod file.

        Args:
            game: Game identifier
            example_name: Name of the example mod

        Returns:
            Full file contents with annotations
        """
        try:
            example_dir = self.schemas_dir / game / "examples" / example_name
            if not example_dir.exists():
                return {
                    "success": False,
                    "error": f"Example mod '{example_name}' not found",
                    "data": None
                }

            files_content = {}
            for file_path in example_dir.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.json', '.xml', '.lua', '.txt']:
                    rel_path = str(file_path.relative_to(example_dir))
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Try to parse JSON for structure
                            if file_path.suffix == '.json':
                                try:
                                    files_content[rel_path] = json.loads(content)
                                except:
                                    files_content[rel_path] = content
                            else:
                                files_content[rel_path] = content
                    except Exception as e:
                        logger.warning(f"Could not read {file_path}: {e}")

            return {
                "success": True,
                "data": files_content,
                "error": None,
                "metadata": {
                    "game": game,
                    "example_name": example_name,
                    "file_count": len(files_content)
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def save_draft(self, game: str, draft_name: str, content: Any) -> Dict[str, Any]:
        """Save work-in-progress content.

        Args:
            game: Game identifier
            draft_name: Name for the draft (e.g., "plan", "v1")
            content: Content to save (can be dict, list, or string)

        Returns:
            Confirmation with draft path
        """
        try:
            draft_key = f"{game}:{draft_name}"
            self.drafts[draft_key] = content

            return {
                "success": True,
                "data": {"draft_key": draft_key, "saved": True},
                "error": None,
                "metadata": {"game": game, "draft_name": draft_name}
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def load_draft(self, game: str, draft_name: str) -> Dict[str, Any]:
        """Load previously saved draft.

        Args:
            game: Game identifier
            draft_name: Name of the draft to load

        Returns:
            Draft content
        """
        try:
            draft_key = f"{game}:{draft_name}"
            if draft_key not in self.drafts:
                return {
                    "success": False,
                    "error": f"Draft '{draft_name}' not found for game '{game}'",
                    "data": None
                }

            return {
                "success": True,
                "data": self.drafts[draft_key],
                "error": None,
                "metadata": {"game": game, "draft_name": draft_name}
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def validate_json(self, content: str) -> Dict[str, Any]:
        """Check if JSON is syntactically valid.

        Args:
            content: JSON string to validate

        Returns:
            Validation result with any errors
        """
        try:
            json.loads(content)
            return {
                "success": True,
                "data": {"valid": True, "errors": []},
                "error": None
            }
        except json.JSONDecodeError as e:
            return {
                "success": True,
                "data": {
                    "valid": False,
                    "errors": [{
                        "message": str(e),
                        "line": e.lineno,
                        "column": e.colno
                    }]
                },
                "error": None
            }
        except Exception as e:
            return {"success": False, "error": str(e), "data": None}

    def search_documentation(self, game: str, query: str) -> Dict[str, Any]:
        """Search game's modding documentation.

        Args:
            game: Game identifier
            query: Search query

        Returns:
            Relevant documentation snippets
        """
        try:
            docs_dir = self.schemas_dir / game / "docs"
            if not docs_dir.exists():
                return {
                    "success": False,
                    "error": f"Documentation directory not found for game: {game}",
                    "data": None
                }

            results = []
            query_lower = query.lower()

            for doc_file in docs_dir.rglob("*"):
                if doc_file.is_file() and doc_file.suffix in ['.md', '.txt']:
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')

                            # Simple search: find lines containing query
                            for i, line in enumerate(lines):
                                if query_lower in line.lower():
                                    # Get context (2 lines before and after)
                                    start = max(0, i - 2)
                                    end = min(len(lines), i + 3)
                                    context = '\n'.join(lines[start:end])

                                    results.append({
                                        "file": doc_file.name,
                                        "line": i + 1,
                                        "context": context
                                    })

                                    # Limit results per file
                                    if len([r for r in results if r["file"] == doc_file.name]) >= 3:
                                        break
                    except Exception as e:
                        logger.warning(f"Could not search {doc_file}: {e}")

            return {
                "success": True,
                "data": results[:10],  # Limit total results
                "error": None,
                "metadata": {
                    "game": game,
                    "query": query,
                    "result_count": len(results)
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": None}
