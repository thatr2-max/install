/**
 * Common Data Loader
 * Loads common data from user-setup.json and applies it to pages
 * This includes contact info, council members, etc.
 */

class CommonDataLoader {
  constructor() {
    this.config = null;
    this.basePath = window.location.pathname.includes('/pages/') ? '../' : '';
  }

  async init() {
    try {
      // Load configuration
      const response = await fetch(`${this.basePath}user-setup.json`);
      if (!response.ok) {
        console.warn('Could not load user-setup.json');
        return;
      }

      this.config = await response.json();

      // Apply contact info to elements
      this.applyContactInfo();

      // Load council members if there's a container for them
      this.loadCouncilMembers();

    } catch (error) {
      console.error('Error initializing common data loader:', error);
    }
  }

  applyContactInfo() {
    if (!this.config.contact_info) return;

    const contactInfo = this.config.contact_info;

    // Apply to elements with data-contact attributes
    this.applyToElements('[data-contact="address"]', contactInfo.city_hall_address);
    this.applyToElements('[data-contact="address_line2"]', contactInfo.city_hall_address_line2);
    this.applyToElements('[data-contact="phone"]', contactInfo.main_phone);
    this.applyToElements('[data-contact="email"]', contactInfo.main_email);
    this.applyToElements('[data-contact="hours"]', contactInfo.office_hours);

    // Apply municipality name
    if (this.config.municipality) {
      this.applyToElements('[data-municipality="name"]', this.config.municipality.name);
    }
  }

  applyToElements(selector, value) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      if (element.tagName === 'A' && element.hasAttribute('href')) {
        // For links, update the href if it's email or phone
        if (selector.includes('email')) {
          element.href = `mailto:${value}`;
          element.textContent = value;
        } else if (selector.includes('phone')) {
          element.href = `tel:${value}`;
          element.textContent = value;
        } else {
          element.textContent = value;
        }
      } else {
        element.textContent = value;
      }
    });
  }

  loadCouncilMembers() {
    const container = document.getElementById('council-members-container');
    if (!container || !this.config.council_members) return;

    const members = this.config.council_members;

    const html = members.map(member => `
      <div class="card">
        <h3>${this.escapeHtml(member.name)}</h3>
        <p><strong>${this.escapeHtml(member.position)}${member.district ? ' - ' + this.escapeHtml(member.district) : ''}</strong></p>
        <p>Email: <a href="mailto:${this.escapeHtml(member.email)}">${this.escapeHtml(member.email)}</a></p>
        <p>Phone: <a href="tel:${this.escapeHtml(member.phone)}">${this.escapeHtml(member.phone)}</a></p>
      </div>
    `).join('');

    container.innerHTML = html;
  }

  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const loader = new CommonDataLoader();
    loader.init();
  });
} else {
  const loader = new CommonDataLoader();
  loader.init();
}
