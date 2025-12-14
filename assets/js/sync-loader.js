/**
 * Sync Service Content Loader
 * Loads server-generated HTML from the sync service
 */

(function() {
    'use strict';

    /**
     * Load content from sync service generated HTML
     * @param {string} folderName - Name of the folder (e.g., 'boards_commissions')
     * @param {string} targetSelector - CSS selector for where to insert content
     */
    function loadSyncContent(folderName, targetSelector) {
        const target = document.querySelector(targetSelector);

        if (!target) {
            console.warn(`Target element not found: ${targetSelector}`);
            return;
        }

        // Show loading state
        target.innerHTML = '<p class="loading"><em>Loading...</em></p>';

        // Fetch the generated HTML file from components directory
        const filePath = `../components/${folderName}.html`;

        fetch(filePath)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Failed to load ${folderName}: ${response.statusText}`);
                }
                return response.text();
            })
            .then(html => {
                // Parse the HTML to extract just the grid content
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const grid = doc.querySelector('.grid');

                if (grid) {
                    // Insert just the grid's inner HTML (the cards)
                    target.innerHTML = grid.innerHTML;
                } else {
                    // Fallback: insert all content from main
                    const main = doc.querySelector('main');
                    if (main) {
                        target.innerHTML = main.innerHTML;
                    } else {
                        target.innerHTML = '<p><em>No content available.</em></p>';
                    }
                }
            })
            .catch(error => {
                console.error(`Error loading ${folderName}:`, error);
                target.innerHTML = `
                    <p><em>Content not yet available.
                    <br>Files from Google Drive will appear here once the sync service has processed them.
                    <br><small>Folder: ${folderName}</small></em></p>
                `;
            });
    }

    /**
     * Load all sync content on page load
     */
    function loadAllSyncContent() {
        // Find all elements with data-drive-folder attribute
        const syncContainers = document.querySelectorAll('[data-drive-folder]');

        syncContainers.forEach(container => {
            const folderName = container.getAttribute('data-drive-folder');
            if (folderName) {
                const targetSelector = `[data-drive-folder="${folderName}"]`;
                loadSyncContent(folderName, targetSelector);
            }
        });
    }

    // Auto-load when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadAllSyncContent);
    } else {
        loadAllSyncContent();
    }

    // Export for manual use
    window.loadSyncContent = loadSyncContent;
})();
