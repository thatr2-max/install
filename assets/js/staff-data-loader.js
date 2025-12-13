/**
 * Staff Directory Data Loader
 * Loads staff information from Google Sheets sync
 */

class StaffDataLoader {
  async init() {
    await this.loadStaffDirectory();
  }

  async loadStaffDirectory() {
    // Try to load the generated staff directory HTML from sync service
    const container = document.getElementById('council-members-container') ||
                     document.getElementById('elected-officials-list') ||
                     document.getElementById('department-heads-list') ||
                     document.getElementById('departments-list');

    if (!container) return;

    try {
      const response = await fetch('../components/staff_directory.html');
      if (!response.ok) {
        console.warn('Staff directory component not found - run sync service to generate');
        this.showFallbackMessage();
        return;
      }

      const html = await response.text();

      // Find all staff containers and populate them
      const containers = [
        'council-members-container',
        'elected-officials-list',
        'department-heads-list',
        'departments-list'
      ];

      containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          el.innerHTML = html;
        }
      });

    } catch (error) {
      console.error('Error loading staff data:', error);
      this.showFallbackMessage();
    }
  }

  showFallbackMessage() {
    const message = '<p><em>Staff directory not configured yet. Run the sync service to populate from Google Sheets.</em></p>';
    const containers = [
      'council-members-container',
      'elected-officials-list',
      'department-heads-list',
      'departments-list'
    ];

    containers.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.innerHTML = message;
      }
    });
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const loader = new StaffDataLoader();
    loader.init();
  });
} else {
  const loader = new StaffDataLoader();
  loader.init();
}
