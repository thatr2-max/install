"""Syntax validation for mod files."""

import json
import logging
from typing import Dict, Any, List
from lxml import etree

logger = logging.getLogger(__name__)


class SyntaxValidator:
    """Validates syntax of mod files."""

    def validate_json(self, content: str) -> Dict[str, Any]:
        """Validate JSON syntax.

        Args:
            content: JSON string to validate

        Returns:
            Validation result with errors if any
        """
        try:
            json.loads(content)
            return {
                "valid": True,
                "errors": []
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [{
                    "type": "JSONDecodeError",
                    "message": str(e),
                    "line": e.lineno,
                    "column": e.colno,
                    "position": e.pos
                }]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [{
                    "type": "UnknownError",
                    "message": str(e)
                }]
            }

    def validate_xml(self, content: str) -> Dict[str, Any]:
        """Validate XML syntax.

        Args:
            content: XML string to validate

        Returns:
            Validation result with errors if any
        """
        try:
            etree.fromstring(content.encode('utf-8'))
            return {
                "valid": True,
                "errors": []
            }
        except etree.XMLSyntaxError as e:
            return {
                "valid": False,
                "errors": [{
                    "type": "XMLSyntaxError",
                    "message": str(e),
                    "line": e.lineno if hasattr(e, 'lineno') else None
                }]
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [{
                    "type": "UnknownError",
                    "message": str(e)
                }]
            }

    def validate_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Validate file based on extension.

        Args:
            file_path: Path to file (used to determine type)
            content: File content

        Returns:
            Validation result
        """
        if file_path.endswith('.json'):
            return self.validate_json(content)
        elif file_path.endswith('.xml'):
            return self.validate_xml(content)
        else:
            # Unknown file type, assume valid
            return {
                "valid": True,
                "errors": [],
                "message": "File type not validated"
            }

    def validate_all_files(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Validate all files in a mod.

        Args:
            files: Dictionary mapping file paths to content

        Returns:
            Overall validation result
        """
        results = {}
        all_valid = True

        for file_path, content in files.items():
            result = self.validate_file(file_path, content)
            results[file_path] = result
            if not result["valid"]:
                all_valid = False

        return {
            "valid": all_valid,
            "file_results": results,
            "error_count": sum(
                len(r.get("errors", []))
                for r in results.values()
            )
        }
