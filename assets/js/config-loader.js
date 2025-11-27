/**
 * Configuration Loader
 * Loads user-setup.json and conditionally displays elements
 */

class ConfigLoader {
  constructor() {
    this.config = null;
    this.init();
  }

  async init() {
    await this.loadConfig();
    this.applyConfig();
  }

  async loadConfig() {
    try {
      const response = await fetch('user-setup.json');
      if (!response.ok) {
        throw new Error('Failed to load configuration');
      }
      this.config = await response.json();
      console.log('Configuration loaded successfully');
    } catch (error) {
      console.error('Error loading configuration:', error);
      // Use default config if loading fails
      this.config = this.getDefaultConfig();
    }
  }

  getDefaultConfig() {
    return {
      municipality: {
        name: "Springfield",
        banner_image: "assets/images/banner.png",
        show_banner: true
      },
      quick_actions: {},
      homepage_cards: {},
      pages: {},
      footer_links: {}
    };
  }

  applyConfig() {
    if (!this.config) return;

    // Apply municipality settings
    this.applyMunicipalitySettings();

    // Apply quick actions visibility
    this.applyQuickActionsVisibility();

    // Apply homepage cards visibility
    this.applyHomepageCardsVisibility();

    // Apply footer links visibility
    this.applyFooterLinksVisibility();

    // Mark configuration as loaded
    document.documentElement.setAttribute('data-config-loaded', 'true');
  }

  applyMunicipalitySettings() {
    const { municipality } = this.config;

    // Update municipality name
    if (municipality.name) {
      const titleElements = document.querySelectorAll('.site-title');
      titleElements.forEach(el => {
        if (el.textContent.includes('City Government Portal')) {
          el.textContent = `${municipality.name} City Government Portal`;
        }
      });

      // Update page titles
      const pageTitle = document.querySelector('title');
      if (pageTitle && municipality.name !== 'Springfield') {
        pageTitle.textContent = pageTitle.textContent.replace('Springfield', municipality.name);
      }
    }

    // Update banner image if on index page
    if (municipality.show_banner && municipality.banner_image) {
      const bannerElement = document.getElementById('municipality-banner');
      if (bannerElement) {
        bannerElement.src = municipality.banner_image;
        bannerElement.style.display = 'block';
      }
    }
  }

  applyQuickActionsVisibility() {
    const { quick_actions } = this.config;

    // Quick action buttons
    const quickActionMap = {
      'permits': 'pages/permits.html',
      'pay_bills': 'pages/pay-bills.html',
      'report_issue': 'pages/report-issue.html',
      'public_records': 'pages/public-records.html'
    };

    Object.entries(quickActionMap).forEach(([key, href]) => {
      const visible = quick_actions[key] !== false;
      const button = document.querySelector(`.quick-action-btn[href="${href}"]`);
      if (button) {
        button.style.display = visible ? '' : 'none';
      }
    });

    // Hide quick actions bar if all actions are hidden
    const visibleActions = Object.values(quick_actions).filter(v => v !== false).length;
    if (visibleActions === 0) {
      const quickActionsBar = document.querySelector('.quick-actions-bar');
      if (quickActionsBar) {
        quickActionsBar.style.display = 'none';
      }
    }
  }

  applyHomepageCardsVisibility() {
    const { homepage_cards } = this.config;

    // Map of card identifiers to their selectors
    const cardMap = {
      'permits_licenses': 'a[href="pages/permits.html"]',
      'pay_bills_taxes': 'a[href="pages/pay-bills.html"]',
      'report_issue': 'a[href="pages/report-issue.html"]',
      'public_records': 'a[href="pages/public-records.html"]',
      'community_events': 'a[href="pages/events.html"]',
      'staff_directory': 'a[href="pages/staff-directory.html"]',
      'careers': 'a[href="pages/careers.html"]',
      'city_council': 'a[href="pages/council-meetings.html"]',
      'public_services': 'a[href="pages/public-services.html"]',
      'parks_recreation': 'a[href="pages/parks-recreation.html"]',
      'public_safety': 'a[href="pages/public-safety.html"]',
      'planning_zoning': 'a[href="pages/planning-zoning.html"]',
      'business_resources': 'a[href="pages/business-resources.html"]',
      'resident_services': 'a[href="pages/resident-services.html"]',
      'faqs': 'a[href="pages/faqs.html"]',
      'news': 'a[href="pages/news.html"]',
      'forms': 'a[href="pages/forms.html"]',
      'contact': 'a[href="pages/contact.html"]'
    };

    Object.entries(cardMap).forEach(([key, selector]) => {
      const visible = homepage_cards[key] !== false;
      const link = document.querySelector(`.grid .card h3 ${selector}`);
      if (link) {
        const card = link.closest('.card');
        if (card) {
          card.style.display = visible ? '' : 'none';
        }
      }
    });
  }

  applyFooterLinksVisibility() {
    const { footer_links } = this.config;

    const footerLinkMap = {
      'accessibility': 'pages/accessibility.html',
      'contact': 'pages/contact.html',
      'faqs': 'pages/faqs.html',
      'careers': 'pages/careers.html',
      'permits': 'pages/permits.html',
      'pay_bills': 'pages/pay-bills.html',
      'report_issue': 'pages/report-issue.html',
      'public_records': 'pages/public-records.html',
      'council_meetings': 'pages/council-meetings.html',
      'staff_directory': 'pages/staff-directory.html',
      'news': 'pages/news.html',
      'forms': 'pages/forms.html'
    };

    Object.entries(footerLinkMap).forEach(([key, href]) => {
      const visible = footer_links[key] !== false;
      const links = document.querySelectorAll(`footer a[href="${href}"]`);
      links.forEach(link => {
        const listItem = link.closest('li');
        if (listItem) {
          listItem.style.display = visible ? '' : 'none';
        }
      });
    });
  }

  // Public method to check if a page should be visible
  isPageVisible(pageKey) {
    if (!this.config || !this.config.pages) return true;
    return this.config.pages[pageKey] !== false;
  }

  // Public method to get municipality name
  getMunicipalityName() {
    return this.config?.municipality?.name || 'Springfield';
  }
}

// Initialize configuration loader
let configLoader;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    configLoader = new ConfigLoader();
  });
} else {
  configLoader = new ConfigLoader();
}

// Export for use in other scripts
window.ConfigLoader = ConfigLoader;
window.configLoader = configLoader;
