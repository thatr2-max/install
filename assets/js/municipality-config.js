/**
 * Municipality Data Loader
 *
 * Automatically loads municipality-specific data into HTML elements.
 * Works with config.js to populate phone numbers, addresses, names, etc.
 *
 * Example usage:
 *   <span data-config="clerk_phone"></span>
 *   <a href="tel:" data-config="clerk_phone" data-config-attr="href" data-config-prefix="tel:"></a>
 *   <span data-config="clerk_phone" data-config-format="phone"></span>
 */

(function() {
    'use strict';

    /**
     * Format values based on type
     */
    function formatValue(value, format) {
        if (!value) return '';

        switch(format) {
            case 'phone':
                // Format phone number for display
                const cleaned = value.replace(/\D/g, '');
                if (cleaned.length === 10) {
                    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
                }
                return value;

            case 'phone-link':
                // Format phone for tel: link
                return value.replace(/\D/g, '');

            case 'email':
                return value.toLowerCase();

            case 'uppercase':
                return value.toUpperCase();

            case 'lowercase':
                return value.toLowerCase();

            case 'title':
                return value.replace(/\w\S*/g, txt =>
                    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
                );

            default:
                return value;
        }
    }

    /**
     * Load config value into element
     */
    function loadConfigValue(element) {
        const configKey = element.getAttribute('data-config');
        const targetAttr = element.getAttribute('data-config-attr');
        const format = element.getAttribute('data-config-format');
        const prefix = element.getAttribute('data-config-prefix') || '';
        const suffix = element.getAttribute('data-config-suffix') || '';

        if (!configKey) return;

        // Get value from config
        let value = MunicipalityConfig[configKey];

        if (value === undefined || value === null || value === '') {
            // Handle missing values
            const fallback = element.getAttribute('data-config-fallback');
            if (fallback) {
                value = fallback;
            } else {
                // Hide element if no value and no fallback
                element.style.display = 'none';
                return;
            }
        }

        // Format the value
        value = formatValue(value, format);

        // Add prefix and suffix
        const finalValue = prefix + value + suffix;

        // Insert into element
        if (targetAttr) {
            // Set as attribute
            element.setAttribute(targetAttr, finalValue);
        } else {
            // Set as text content
            element.textContent = finalValue;
        }

        // Show element if it was hidden
        element.style.display = '';
    }

    /**
     * Load all config values on page
     */
    function loadAllConfigValues() {
        const elements = document.querySelectorAll('[data-config]');
        elements.forEach(loadConfigValue);
    }

    /**
     * Helper function to get config value in JavaScript
     */
    window.getConfig = function(key, defaultValue = '') {
        return MunicipalityConfig[key] || defaultValue;
    };

    /**
     * Helper function to check if config value exists
     */
    window.hasConfig = function(key) {
        const value = MunicipalityConfig[key];
        return value !== undefined && value !== null && value !== '';
    };

    // Load config values when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAllConfigValues);
    } else {
        loadAllConfigValues();
    }

    // Re-run after dynamic content loads (useful for AJAX-loaded content)
    window.reloadMunicipalityConfig = loadAllConfigValues;

})();
