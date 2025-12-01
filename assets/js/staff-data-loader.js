/**
 * Staff Directory Data Loader
 * Loads staff information from user-setup.json
 */

class StaffDataLoader {
  constructor() {
    this.config = null;
  }

  async init() {
    try {
      const response = await fetch('../user-setup.json');
      if (!response.ok) {
        console.warn('Could not load user-setup.json');
        return;
      }

      this.config = await response.json();
      this.loadElectedOfficials();
      this.loadDepartmentHeads();
      this.loadDepartments();
    } catch (error) {
      console.error('Error loading staff data:', error);
    }
  }

  loadElectedOfficials() {
    const container = document.getElementById('elected-officials-list');
    if (!container || !this.config.staff || !this.config.staff.elected_officials) return;

    const officials = this.config.staff.elected_officials;
    if (officials.length === 0) {
      container.innerHTML = '<p><em>No other elected officials configured yet. Add elected officials in the setup wizard.</em></p>';
      return;
    }

    const html = officials.map(official => `
      <div class="card">
        <h3>${this.escapeHtml(official.name)}</h3>
        <p><strong>${this.escapeHtml(official.title)}</strong></p>
        ${official.email ? `<p>Email: <a href="mailto:${this.escapeHtml(official.email)}">${this.escapeHtml(official.email)}</a></p>` : ''}
        ${official.phone ? `<p>Phone: <a href="tel:${this.escapeHtml(official.phone)}">${this.escapeHtml(official.phone)}</a></p>` : ''}
      </div>
    `).join('');

    container.innerHTML = html;
  }

  loadDepartmentHeads() {
    const container = document.getElementById('department-heads-list');
    if (!container || !this.config.staff || !this.config.staff.department_heads) return;

    const heads = this.config.staff.department_heads;
    if (heads.length === 0) {
      container.innerHTML = '<p><em>No department heads configured yet. Add department heads in the setup wizard.</em></p>';
      return;
    }

    const html = heads.map(head => `
      <div class="card">
        <h3>${this.escapeHtml(head.name)}</h3>
        <p><strong>${this.escapeHtml(head.title)}</strong></p>
        ${head.department ? `<p><em>${this.escapeHtml(head.department)}</em></p>` : ''}
        ${head.email ? `<p>Email: <a href="mailto:${this.escapeHtml(head.email)}">${this.escapeHtml(head.email)}</a></p>` : ''}
        ${head.phone ? `<p>Phone: <a href="tel:${this.escapeHtml(head.phone)}">${this.escapeHtml(head.phone)}</a></p>` : ''}
      </div>
    `).join('');

    container.innerHTML = html;
  }

  loadDepartments() {
    const container = document.getElementById('departments-list');
    if (!container || !this.config.staff || !this.config.staff.departments) return;

    const departments = this.config.staff.departments;
    if (departments.length === 0) {
      container.innerHTML = '<p><em>No departments configured yet. Add departments in the setup wizard.</em></p>';
      return;
    }

    const html = departments.map(dept => `
      <div class="card">
        <h3>${this.escapeHtml(dept.name)}</h3>
        ${dept.location ? `<p><strong>Location:</strong> ${this.escapeHtml(dept.location)}</p>` : ''}
        ${dept.phone ? `<p><strong>Phone:</strong> <a href="tel:${this.escapeHtml(dept.phone)}">${this.escapeHtml(dept.phone)}</a></p>` : ''}
        ${dept.email ? `<p><strong>Email:</strong> <a href="mailto:${this.escapeHtml(dept.email)}">${this.escapeHtml(dept.email)}</a></p>` : ''}
        ${dept.hours ? `<p><strong>Hours:</strong> ${this.escapeHtml(dept.hours)}</p>` : ''}
        ${dept.services && dept.services.length > 0 ? `
          <p><strong>Services:</strong></p>
          <ul>
            ${dept.services.map(s => `<li>${this.escapeHtml(s)}</li>`).join('')}
          </ul>
        ` : ''}
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
    const loader = new StaffDataLoader();
    loader.init();
  });
} else {
  const loader = new StaffDataLoader();
  loader.init();
}
