/**
 * Head Loader - Dynamically generates <head> content
 * This script runs immediately to populate the <head> section
 * before the page renders, minimizing visual flash.
 */

(function() {
  // Get page-specific config (set in each page)
  const config = window.pageConfig || {
    title: 'Springfield City Government Portal',
    description: 'Accessible government services portal',
    isHomePage: false
  };

  // Determine base path (for pages in subdirectory)
  const basePath = config.isHomePage ? '' : '../';

  // Build the head content
  const headContent = `
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${config.description}">
    <title>${config.title}</title>
    <link rel="stylesheet" href="${basePath}assets/css/styles.css">
    <link rel="stylesheet" href="${basePath}assets/css/accessibility-widget.css">
    ${config.isHomePage ? '<script src="assets/js/config-loader.js"><\/script>' : ''}
  `;

  // Inject into head
  document.head.innerHTML += headContent;
})();
