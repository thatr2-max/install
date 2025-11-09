"""Schema learning from example mods and documentation."""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import Counter, defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SchemaLearner:
    """Learn modding patterns from example mods."""

    def __init__(self, game_schema_dir: Path):
        """Initialize schema learner for a specific game.

        Args:
            game_schema_dir: Directory containing game's examples, docs, etc.
        """
        self.game_schema_dir = Path(game_schema_dir)
        self.examples_dir = self.game_schema_dir / "examples"
        self.docs_dir = self.game_schema_dir / "docs"
        self.vanilla_data_dir = self.game_schema_dir / "vanilla_data"
        self.game_name = self.game_schema_dir.name

    def analyze_examples(self) -> Dict[str, Any]:
        """Analyze example mods to extract structural patterns.

        Returns:
            Dictionary containing extracted patterns and statistics
        """
        if not self.examples_dir.exists():
            raise FileNotFoundError(f"Examples directory not found: {self.examples_dir}")

        logger.info(f"Analyzing examples in {self.examples_dir}")

        patterns = {
            "file_types": Counter(),
            "templates": defaultdict(lambda: {
                "fields": Counter(),
                "required_fields": set(),
                "optional_fields": set(),
                "data_types": {},
                "common_values": defaultdict(Counter),
                "examples": []
            }),
            "naming_conventions": {},
            "file_structure": [],
            "total_files": 0,
            "total_mods": 0
        }

        # Scan all example mods
        mod_dirs = [d for d in self.examples_dir.iterdir() if d.is_dir()]
        patterns["total_mods"] = len(mod_dirs)

        for mod_dir in mod_dirs:
            self._analyze_mod_directory(mod_dir, patterns)

        # Post-process to determine required vs optional fields
        for template_name, template_data in patterns["templates"].items():
            self._determine_required_fields(template_data)

        logger.info(f"Analyzed {patterns['total_files']} files from {patterns['total_mods']} mods")
        return patterns

    def _analyze_mod_directory(self, mod_dir: Path, patterns: Dict[str, Any]):
        """Analyze a single mod directory."""
        for file_path in mod_dir.rglob("*"):
            if not file_path.is_file():
                continue

            patterns["total_files"] += 1
            file_ext = file_path.suffix.lower()
            patterns["file_types"][file_ext] += 1

            # Analyze based on file type
            if file_ext == ".json":
                self._analyze_json_file(file_path, patterns)
            elif file_ext == ".xml":
                self._analyze_xml_file(file_path, patterns)
            # Add more file type handlers as needed

    def _analyze_json_file(self, file_path: Path, patterns: Dict[str, Any]):
        """Analyze a JSON mod file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both single objects and arrays
            items = data if isinstance(data, list) else [data]

            for item in items:
                if not isinstance(item, dict):
                    continue

                # Determine template type (e.g., "item", "recipe", etc.)
                template_type = self._infer_template_type(item, file_path)
                template = patterns["templates"][template_type]

                # Analyze fields
                self._analyze_fields(item, template)

                # Store example (limit to first 3 per template)
                if len(template["examples"]) < 3:
                    template["examples"].append(item)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

    def _analyze_xml_file(self, file_path: Path, patterns: Dict[str, Any]):
        """Analyze an XML mod file."""
        # Placeholder for XML analysis
        # Would use lxml to parse and extract patterns
        logger.debug(f"XML analysis not yet implemented for {file_path}")

    def _infer_template_type(self, item: Dict[str, Any], file_path: Path) -> str:
        """Infer the template type from item content and file path."""
        # Check for explicit type field
        if "type" in item:
            return item["type"].lower()

        # Infer from file path
        path_parts = file_path.parts
        for part in reversed(path_parts):
            if part in ["items", "recipes", "monsters", "professions", "weapons"]:
                return part.rstrip('s')  # Singular form

        # Default to generic based on file name
        return file_path.stem.lower()

    def _analyze_fields(self, item: Dict[str, Any], template: Dict[str, Any], prefix: str = ""):
        """Recursively analyze fields in an item."""
        for key, value in item.items():
            field_path = f"{prefix}.{key}" if prefix else key
            template["fields"][field_path] += 1

            # Track data type
            value_type = type(value).__name__
            if field_path not in template["data_types"]:
                template["data_types"][field_path] = value_type
            elif template["data_types"][field_path] != value_type:
                template["data_types"][field_path] = "mixed"

            # Track common values for strings and small integers
            if isinstance(value, str) or (isinstance(value, int) and abs(value) < 1000):
                template["common_values"][field_path][value] += 1

            # Recurse into nested objects
            if isinstance(value, dict):
                self._analyze_fields(value, template, field_path)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                # Analyze first item in array as representative
                self._analyze_fields(value[0], template, f"{field_path}[]")

    def _determine_required_fields(self, template: Dict[str, Any]):
        """Determine which fields are required vs optional.

        A field is considered required if it appears in >80% of examples.
        """
        total_occurrences = max(template["fields"].values()) if template["fields"] else 1
        threshold = 0.8

        for field, count in template["fields"].items():
            frequency = count / total_occurrences
            if frequency >= threshold:
                template["required_fields"].add(field)
            else:
                template["optional_fields"].add(field)

        # Convert sets to lists for JSON serialization
        template["required_fields"] = sorted(list(template["required_fields"]))
        template["optional_fields"] = sorted(list(template["optional_fields"]))

    def generate_schema(self, patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema from analyzed patterns.

        Args:
            patterns: Patterns extracted from analyze_examples()

        Returns:
            Complete schema dictionary
        """
        schema = {
            "game": self.game_name,
            "version": "1.0",
            "learned_at": datetime.now().isoformat(),
            "example_count": patterns["total_mods"],
            "file_types": [ft for ft in patterns["file_types"].keys()],
            "mod_structure": {
                "file_types_distribution": dict(patterns["file_types"])
            },
            "templates": {}
        }

        # Convert templates to schema format
        for template_name, template_data in patterns["templates"].items():
            schema["templates"][template_name] = {
                "required_fields": template_data["required_fields"],
                "optional_fields": template_data["optional_fields"],
                "field_descriptions": {},  # To be filled from docs
                "data_types": template_data["data_types"],
                "common_values": {
                    field: dict(values.most_common(10))
                    for field, values in template_data["common_values"].items()
                },
                "examples": template_data["examples"]
            }

        return schema

    def save_schema(self, schema: Dict[str, Any]):
        """Save schema to file."""
        schema_path = self.game_schema_dir / "schema.json"
        with open(schema_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, default=str)
        logger.info(f"Schema saved to {schema_path}")

        # Create summary
        self._create_schema_summary(schema)

    def _create_schema_summary(self, schema: Dict[str, Any]):
        """Create a human-readable schema summary."""
        summary_path = self.game_schema_dir / "schema_summary.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Schema Summary for {schema['game']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {schema['learned_at']}\n")
            f.write(f"Example Mods Analyzed: {schema['example_count']}\n")
            f.write(f"File Types: {', '.join(schema['file_types'])}\n\n")
            f.write("Templates Found:\n")
            f.write("-" * 50 + "\n")

            for template_name, template in schema["templates"].items():
                f.write(f"\n{template_name.upper()}\n")
                f.write(f"  Required fields: {', '.join(template['required_fields'][:5])}")
                if len(template['required_fields']) > 5:
                    f.write(f" ... (+{len(template['required_fields']) - 5} more)")
                f.write("\n")
                f.write(f"  Optional fields: {len(template['optional_fields'])}\n")

        logger.info(f"Summary saved to {summary_path}")

    def learn(self) -> Dict[str, Any]:
        """Main learning pipeline: analyze examples and generate schema.

        Returns:
            Generated schema
        """
        logger.info(f"Starting schema learning for {self.game_name}")

        # Analyze examples
        patterns = self.analyze_examples()

        # Generate schema
        schema = self.generate_schema(patterns)

        # Save schema
        self.save_schema(schema)

        return schema
