/**
 * Form Configuration Loader
 * Loads form submission email from user-setup.json
 * Updates all forms on the page to use the configured email
 */

(function() {
  async function loadFormConfig() {
    try {
      // Determine base path
      const isSubpage = window.location.pathname.includes('/pages/');
      const basePath = isSubpage ? '../' : '';

      // Load configuration
      const response = await fetch(`${basePath}user-setup.json`);
      if (!response.ok) {
        console.warn('Could not load user-setup.json, forms will use default config');
        return;
      }

      const config = await response.json();
      const email = config.form_submissions?.default_email || 'admin@citygovernment.gov';

      // Update all forms on the page
      const forms = document.querySelectorAll('form');
      forms.forEach(form => {
        // Only update forms that point to formsubmit.co
        const currentAction = form.getAttribute('action') || '';
        if (currentAction.includes('formsubmit.co')) {
          form.setAttribute('action', `https://formsubmit.co/${email}`);
        }
      });

      console.log(`Forms configured to send to: ${email}`);

    } catch (error) {
      console.error('Error loading form configuration:', error);
    }
  }

  // Load config when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadFormConfig);
  } else {
    loadFormConfig();
  }
})();
