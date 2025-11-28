/**
 * Component Loader - Loads header and footer components
 * Automatically detects if on home page or subpage and loads appropriate header
 */

class ComponentLoader {
  constructor() {
    this.isHomePage = window.location.pathname.endsWith('index.html') ||
                      window.location.pathname.endsWith('/') ||
                      window.location.pathname === '/install/';
    this.basePath = this.isHomePage ? '' : '../';
    this.init();
  }

  async init() {
    try {
      await Promise.all([
        this.loadHeader(),
        this.loadFooter()
      ]);
    } catch (error) {
      console.error('Error loading components:', error);
    }
  }

  async loadHeader() {
    const headerElement = document.getElementById('header');
    if (!headerElement) return;

    const headerFile = this.isHomePage ? 'header-home.html' : 'header-page.html';
    const headerPath = `${this.basePath}components/${headerFile}`;

    try {
      const response = await fetch(headerPath);
      if (!response.ok) throw new Error(`Failed to load header: ${response.status}`);

      const html = await response.text();
      headerElement.innerHTML = html;
    } catch (error) {
      console.error('Error loading header:', error);
      // Fallback: show minimal header
      headerElement.innerHTML = '<p>Navigation could not be loaded</p>';
    }
  }

  async loadFooter() {
    const footerElement = document.getElementById('footer');
    if (!footerElement) return;

    const footerPath = `${this.basePath}components/footer.html`;

    try {
      const response = await fetch(footerPath);
      if (!response.ok) throw new Error(`Failed to load footer: ${response.status}`);

      let html = await response.text();

      // Fix script path for subpages
      html = html.replace('SCRIPT_PATH_PLACEHOLDER', this.basePath);

      // Fix footer links for home page vs subpages
      if (this.isHomePage) {
        // On home page, links should go to pages/ directory
        // Links are already correct in footer.html
      } else {
        // On subpages, links are already relative (no ../)
        // Links in footer.html already point to correct relative paths
      }

      footerElement.innerHTML = html;
    } catch (error) {
      console.error('Error loading footer:', error);
      // Fallback: show minimal footer
      footerElement.innerHTML = '<p>&copy; 2025 City Government</p>';
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new ComponentLoader();
  });
} else {
  new ComponentLoader();
}
