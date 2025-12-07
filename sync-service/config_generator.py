"""
Config Generator
Generates config.js file from Google Sheets data
"""

import logging
import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger('config_generator')


class ConfigGenerator:
    """Generates JavaScript config file from sheet data"""

    def __init__(self, output_dir: Path):
        """
        Initialize config generator

        Args:
            output_dir: Directory to output config.js file (usually assets/js/)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_config_js(self, config_data: Dict[str, Any]) -> str:
        """
        Generate config.js content from config data

        Args:
            config_data: Dict of configuration values

        Returns:
            JavaScript file content as string
        """
        # Start with file header
        js_content = '''/**
 * Municipality Configuration
 *
 * This file is AUTO-GENERATED from Google Sheets.
 * DO NOT EDIT MANUALLY - Your changes will be overwritten!
 *
 * To update configuration, edit the Municipality Config Google Sheet.
 * Generated: {timestamp}
 */

const MunicipalityConfig = {{
'''.format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Add each config value
        for key, value in sorted(config_data.items()):
            if isinstance(value, dict):
                # Handle nested objects (google_drive_folders, google_sheets)
                js_content += f'    {key}: {{\n'
                for sub_key, sub_value in sorted(value.items()):
                    js_content += f'        {sub_key}: "{self._escape_js_string(sub_value)}",\n'
                js_content += '    },\n\n'
            elif isinstance(value, bool):
                # Boolean values
                js_content += f'    {key}: {str(value).lower()},\n'
            elif isinstance(value, (int, float)):
                # Numeric values
                js_content += f'    {key}: {value},\n'
            else:
                # String values (most common)
                js_content += f'    {key}: "{self._escape_js_string(str(value))}",\n'

        # Close the object
        js_content += '''};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MunicipalityConfig;
}
'''

        return js_content

    def _escape_js_string(self, value: str) -> str:
        """
        Escape string for use in JavaScript

        Args:
            value: String to escape

        Returns:
            Escaped string safe for JS
        """
        # Replace special characters
        value = value.replace('\\', '\\\\')  # Backslash
        value = value.replace('"', '\\"')    # Double quote
        value = value.replace("'", "\\'")    # Single quote
        value = value.replace('\n', '\\n')   # Newline
        value = value.replace('\r', '\\r')   # Carriage return
        value = value.replace('\t', '\\t')   # Tab
        return value

    def save_config_js(self, config_data: Dict[str, Any]) -> bool:
        """
        Generate and save config.js file

        Args:
            config_data: Dict of configuration values

        Returns:
            True if successful, False otherwise
        """
        try:
            js_content = self.generate_config_js(config_data)
            output_file = self.output_dir / 'config.js'

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(js_content)

            logger.info(f"Generated config.js: {output_file} ({len(config_data)} config values)")
            return True

        except Exception as e:
            logger.error(f"Failed to save config.js: {e}")
            return False

    def save_config_json(self, config_data: Dict[str, Any]) -> bool:
        """
        Also save as JSON for easier debugging/inspection

        Args:
            config_data: Dict of configuration values

        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = self.output_dir / 'config.json'

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Generated config.json: {output_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save config.json: {e}")
            return False
