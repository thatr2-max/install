/**
 * Configuration Builder
 * Visual tool for creating user-setup.json configuration
 */

class ConfigBuilder {
  constructor() {
    this.config = {
      municipality: {
        name: "Springfield",
        banner_image: "assets/images/banner.svg",
        show_banner: true
      },
      quick_actions: {},
      homepage_cards: {},
      footer_links: {}
    };

    this.stats = {
      quick_actions: { included: 0, total: 0 },
      cards: { included: 0, total: 0 },
      footer: { included: 0, total: 0 }
    };

    this.init();
  }

  init() {
    // Load existing configuration if available
    this.loadExistingConfig();

    // Initialize all configurable elements
    this.initializeElements();

    // Attach event listeners
    this.attachEventListeners();

    // Update statistics
    this.updateStats();
  }

  async loadExistingConfig() {
    try {
      const response = await fetch('user-setup.json');
      if (response.ok) {
        const existingConfig = await response.json();
        this.config = existingConfig;
        console.log('Loaded existing configuration');
      }
    } catch (error) {
      console.log('No existing config found, using defaults');
    }
  }

  initializeElements() {
    // Find all configurable elements
    const elements = document.querySelectorAll('.configurable-element');

    elements.forEach(element => {
      const type = element.dataset.configType;
      const id = element.dataset.configId;

      if (!type || !id) return;

      // Initialize config section if not exists
      if (!this.config[type]) {
        this.config[type] = {};
      }

      // Set default value if not already set
      if (this.config[type][id] === undefined) {
        this.config[type][id] = true;
      }

      // Apply current state
      if (!this.config[type][id]) {
        element.classList.add('excluded');
        this.addExclusionBadge(element);
      }

      // Track totals
      this.incrementTotal(type);
      if (this.config[type][id]) {
        this.incrementIncluded(type);
      }
    });
  }

  attachEventListeners() {
    const elements = document.querySelectorAll('.configurable-element');

    elements.forEach(element => {
      element.addEventListener('dblclick', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.toggleElement(element);
      });

      // Visual feedback on single click
      element.addEventListener('click', (e) => {
        if (!element.classList.contains('excluded')) {
          element.style.transform = 'scale(0.98)';
          setTimeout(() => {
            element.style.transform = '';
          }, 100);
        }
      });
    });
  }

  toggleElement(element) {
    const type = element.dataset.configType;
    const id = element.dataset.configId;

    if (!type || !id) return;

    // Toggle state
    const currentState = this.config[type][id];
    this.config[type][id] = !currentState;

    // Update visual state
    if (this.config[type][id]) {
      // Include element
      element.classList.remove('excluded');
      this.removeExclusionBadge(element);
      this.incrementIncluded(type);
    } else {
      // Exclude element
      element.classList.add('excluded');
      this.addExclusionBadge(element);
      this.decrementIncluded(type);
    }

    // Update statistics display
    this.updateStats();

    // Visual feedback
    this.showToggleFeedback(element);
  }

  addExclusionBadge(element) {
    // Check if badge already exists
    if (element.querySelector('.exclusion-badge')) return;

    const badge = document.createElement('div');
    badge.className = 'exclusion-badge';
    badge.textContent = 'EXCLUDED';
    element.style.position = 'relative';
    element.appendChild(badge);
  }

  removeExclusionBadge(element) {
    const badge = element.querySelector('.exclusion-badge');
    if (badge) {
      badge.remove();
    }
  }

  showToggleFeedback(element) {
    const isIncluded = !element.classList.contains('excluded');
    const feedback = document.createElement('div');
    feedback.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: ${isIncluded ? '#48bb78' : '#f56565'};
      color: white;
      padding: 1rem 2rem;
      border-radius: 8px;
      font-size: 1.2rem;
      font-weight: bold;
      z-index: 10000;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
      animation: fadeInOut 0.8s ease;
    `;
    feedback.textContent = isIncluded ? '✓ INCLUDED' : '✕ EXCLUDED';

    document.body.appendChild(feedback);

    setTimeout(() => {
      feedback.remove();
    }, 800);
  }

  incrementTotal(type) {
    const statType = this.getStatType(type);
    if (statType) {
      this.stats[statType].total++;
    }
  }

  incrementIncluded(type) {
    const statType = this.getStatType(type);
    if (statType) {
      this.stats[statType].included++;
    }
  }

  decrementIncluded(type) {
    const statType = this.getStatType(type);
    if (statType) {
      this.stats[statType].included--;
    }
  }

  getStatType(configType) {
    const mapping = {
      'quick_actions': 'quick_actions',
      'homepage_cards': 'cards',
      'footer_links': 'footer'
    };
    return mapping[configType];
  }

  updateStats() {
    // Update Quick Actions stat
    const qaElement = document.getElementById('stat-quick-actions');
    if (qaElement) {
      qaElement.textContent = `${this.stats.quick_actions.included} / ${this.stats.quick_actions.total}`;
    }

    // Update Cards stat
    const cardsElement = document.getElementById('stat-cards');
    if (cardsElement) {
      cardsElement.textContent = `${this.stats.cards.included} / ${this.stats.cards.total}`;
    }

    // Update Footer stat
    const footerElement = document.getElementById('stat-footer');
    if (footerElement) {
      footerElement.textContent = `${this.stats.footer.included} / ${this.stats.footer.total}`;
    }
  }

  resetAll() {
    // Confirm with user
    if (!confirm('Reset all elements to INCLUDED? This will undo all exclusions.')) {
      return;
    }

    // Reset all config values to true
    Object.keys(this.config.quick_actions).forEach(key => {
      this.config.quick_actions[key] = true;
    });
    Object.keys(this.config.homepage_cards).forEach(key => {
      this.config.homepage_cards[key] = true;
    });
    Object.keys(this.config.footer_links).forEach(key => {
      this.config.footer_links[key] = true;
    });

    // Reset visual state
    const elements = document.querySelectorAll('.configurable-element');
    elements.forEach(element => {
      element.classList.remove('excluded');
      this.removeExclusionBadge(element);
    });

    // Reset stats
    this.stats.quick_actions.included = this.stats.quick_actions.total;
    this.stats.cards.included = this.stats.cards.total;
    this.stats.footer.included = this.stats.footer.total;

    this.updateStats();

    // Show feedback
    const feedback = document.createElement('div');
    feedback.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #4299e1;
      color: white;
      padding: 1.5rem 3rem;
      border-radius: 8px;
      font-size: 1.3rem;
      font-weight: bold;
      z-index: 10000;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    `;
    feedback.textContent = '🔄 All elements reset to INCLUDED';
    document.body.appendChild(feedback);
    setTimeout(() => feedback.remove(), 1500);
  }

  downloadConfig() {
    // Create configuration object
    const configOutput = {
      municipality: this.config.municipality,
      quick_actions: this.config.quick_actions,
      homepage_cards: this.config.homepage_cards,
      pages: this.config.pages || {
        "accessibility": true,
        "contact": true,
        "permits": true,
        "pay_bills": true,
        "report_issue": true,
        "public_records": true,
        "events": true,
        "staff_directory": true,
        "careers": true,
        "council_meetings": true,
        "public_services": true,
        "parks_recreation": true,
        "public_safety": true,
        "planning_zoning": true,
        "business_resources": true,
        "resident_services": true,
        "faqs": true,
        "news": true,
        "forms": true,
        "311_services": true,
        "animal_control": true,
        "boards_commissions": true,
        "budget_finance": true,
        "building_inspections": true,
        "business_licenses": true,
        "city_council": true,
        "code_enforcement": true,
        "community_development": true,
        "economic_development": true,
        "education": true,
        "emergency_management": true,
        "environmental_services": true,
        "garbage_recycling": true,
        "gis_maps": true,
        "health_department": true,
        "historic_preservation": true,
        "housing_authority": true,
        "human_services": true,
        "legal": true,
        "library": true,
        "municipal_court": true,
        "neighborhood_services": true,
        "notary_services": true,
        "open_data": true,
        "parking_services": true,
        "privacy_policy": true,
        "property_assessor": true,
        "public_works_projects": true,
        "real_estate": true,
        "senior_services": true,
        "sitemap": true,
        "social_services": true,
        "street_maintenance": true,
        "streets_traffic": true,
        "sustainability": true,
        "tax_information": true,
        "tourism": true,
        "transportation": true,
        "utilities": true,
        "veterans_services": true,
        "volunteer": true,
        "voting_elections": true,
        "water_sewer": true,
        "weather_alerts": true,
        "youth_services": true,
        "zoning_appeals": true
      },
      footer_links: this.config.footer_links
    };

    // Convert to JSON string with formatting
    const jsonString = JSON.stringify(configOutput, null, 2);

    // Create blob and download
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'user-setup.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // Show success message
    const feedback = document.createElement('div');
    feedback.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: #48bb78;
      color: white;
      padding: 1.5rem 3rem;
      border-radius: 8px;
      font-size: 1.3rem;
      font-weight: bold;
      z-index: 10000;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    `;
    feedback.innerHTML = '💾 Configuration downloaded!<br><small style="font-size: 0.8rem; font-weight: normal;">Replace your user-setup.json file with this download</small>';
    document.body.appendChild(feedback);
    setTimeout(() => feedback.remove(), 3000);
  }

  exitBuilder() {
    if (confirm('Exit builder mode and return to homepage?')) {
      window.location.href = 'index.html';
    }
  }
}

// Add CSS animation for feedback
const style = document.createElement('style');
style.textContent = `
  @keyframes fadeInOut {
    0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
    20% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
    80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    100% { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
  }
`;
document.head.appendChild(style);

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.configBuilder = new ConfigBuilder();
  });
} else {
  window.configBuilder = new ConfigBuilder();
}
