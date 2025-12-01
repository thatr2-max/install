/**
 * Parks Data Loader
 * Loads parks and trails from user-setup.json
 */

class ParksDataLoader {
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
      this.loadParks();
      this.loadTrails();
      this.loadCommunityCenter();
    } catch (error) {
      console.error('Error loading parks data:', error);
    }
  }

  loadParks() {
    const container = document.getElementById('parks-list');
    if (!container || !this.config.parks) return;

    const parks = this.config.parks;
    if (parks.length === 0) {
      container.innerHTML = '<p><em>No parks configured yet. Add parks in the setup wizard.</em></p>';
      return;
    }

    const html = parks.map(park => `
      <div class="card">
        <h3>${this.escapeHtml(park.name)}</h3>
        <p><strong>Location:</strong> ${this.escapeHtml(park.location)}</p>
        <p><strong>Size:</strong> ${this.escapeHtml(park.size)} acres</p>
        ${park.amenities && park.amenities.length > 0 ? `
          <p><strong>Amenities:</strong></p>
          <ul>
            ${park.amenities.map(a => `<li>${this.escapeHtml(a)}</li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `).join('');

    container.innerHTML = html;
  }

  loadTrails() {
    const container = document.getElementById('trails-list');
    if (!container || !this.config.trails) return;

    const trails = this.config.trails;
    if (trails.length === 0) {
      container.innerHTML = '<p><em>No trails configured yet. Add trails in the setup wizard.</em></p>';
      return;
    }

    const html = trails.map(trail => `
      <div class="card">
        <h3>${this.escapeHtml(trail.name)}</h3>
        <p><strong>Length:</strong> ${this.escapeHtml(trail.length)}</p>
        <p><strong>Surface:</strong> ${this.escapeHtml(trail.surface)}</p>
        ${trail.features && trail.features.length > 0 ? `
          <p><strong>Features:</strong></p>
          <ul>
            ${trail.features.map(f => `<li>${this.escapeHtml(f)}</li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `).join('');

    container.innerHTML = html;
  }

  loadCommunityCenter() {
    const container = document.getElementById('community-center-info');
    if (!container || !this.config.community_center) return;

    const cc = this.config.community_center;
    if (!cc.name) {
      container.innerHTML = '<p><em>No community center configured yet. Add community center information in the setup wizard.</em></p>';
      return;
    }

    const html = `
      <div style="margin-bottom: 1.5rem;">
        <p><strong>Name:</strong> ${this.escapeHtml(cc.name)}</p>
        ${cc.address ? `<p><strong>Address:</strong> ${this.escapeHtml(cc.address)}</p>` : ''}
        ${cc.phone ? `<p><strong>Phone:</strong> <a href="tel:${this.escapeHtml(cc.phone)}">${this.escapeHtml(cc.phone)}</a></p>` : ''}
        ${cc.hours ? `<p><strong>Hours:</strong> ${this.escapeHtml(cc.hours)}</p>` : ''}
        ${cc.amenities && cc.amenities.length > 0 ? `
          <p><strong>Facilities:</strong></p>
          <ul>
            ${cc.amenities.map(a => `<li>${this.escapeHtml(a)}</li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `;

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
    const loader = new ParksDataLoader();
    loader.init();
  });
} else {
  const loader = new ParksDataLoader();
  loader.init();
}
