/**
 * Accessibility Widget
 * Provides site-wide accessibility controls
 */

class AccessibilityWidget {
  constructor() {
    this.settings = this.loadSettings();
    this.init();
  }

  init() {
    this.createWidget();
    this.applySettings();
    this.attachEventListeners();
  }

 loadSettings() {
    const defaults = {
      fontSize: 'normal',
      lineHeight: 'normal',
      letterSpacing: 'normal',
      saturation: 'normal',
      dyslexicFont: false,
      highlightLinks: false
    };

    try {
      const saved = localStorage.getItem('accessibilitySettings');
      return saved ? { ...defaults, ...JSON.parse(saved) } : defaults;
    } catch (e) {
      return defaults;
    }
  }

  saveSettings() {
    try {
      localStorage.setItem('accessibilitySettings', JSON.stringify(this.settings));
    } catch (e) {
      console.error('Failed to save accessibility settings', e);
    }
  }

  createWidget() {
    const widget = document.createElement('div');
    widget.id = 'accessibility-widget';
    widget.innerHTML = `
      <button id="accessibility-toggle" class="accessibility-toggle" aria-label="Accessibility Options" aria-expanded="false">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
        </svg>
        <span class="accessibility-toggle-text">Accessibility</span>
      </button>
      <div id="accessibility-panel" class="accessibility-panel" aria-hidden="true">
        <div class="accessibility-panel-header">
          <h2>Accessibility Options</h2>
          <button id="accessibility-close" class="accessibility-close" aria-label="Close accessibility panel">×</button>
        </div>
        <div class="accessibility-panel-content">

          <div class="accessibility-group">
            <h3>Text Size</h3>
            <div class="accessibility-buttons">
              <button data-setting="fontSize" data-value="normal" aria-label="Normal text" class="active">A</button>
              <button data-setting="fontSize" data-value="large" aria-label="Large text">A</button>
              <button data-setting="fontSize" data-value="xlarge" aria-label="Extra large text">A</button>
            </div>
          </div>

         <div class="accessibility-group">
            <h3>Saturation</h3>
            <div class="accessibility-buttons">
              <button data-setting="saturation" data-value="normal" class="active">Normal</button>
              <button data-setting="saturation" data-value="reduced">Reduced</button>
              <button data-setting="saturation" data-value="grayscale">Grayscale</button>
            </div>
          </div>

          <div class="accessibility-group">
            <h3>Line Height</h3>
            <div class="accessibility-buttons">
              <button data-setting="lineHeight" data-value="normal" class="active">Normal</button>
              <button data-setting="lineHeight" data-value="comfortable">Comfortable</button>
              <button data-setting="lineHeight" data-value="spacious">Spacious</button>
            </div>
          </div>

        <div class="accessibility-group">
            <h3>Letter Spacing</h3>
            <div class="accessibility-buttons">
              <button data-setting="letterSpacing" data-value="normal" class="active">Normal</button>
              <button data-setting="letterSpacing" data-value="light">Light</button>
              <button data-setting="letterSpacing" data-value="moderate">Moderate</button>
              <button data-setting="letterSpacing" data-value="heavy">Heavy</button>
            </div>
          </div>

          <div class="accessibility-group">
            <h3>Visual Options</h3>
            <label class="accessibility-checkbox">
              <input type="checkbox" data-setting="dyslexicFont">
              <span>Dyslexia-Friendly Font</span>
            </label>
            <label class="accessibility-checkbox">
              <input type="checkbox" data-setting="highlightLinks">
              <span>Highlight Links</span>
            </label>
          </div>

          <div class="accessibility-group">
            <button id="accessibility-reset" class="accessibility-reset-btn">Reset to Defaults</button>
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(widget);
  }

  attachEventListeners() {
    const toggle = document.getElementById('accessibility-toggle');
    const panel = document.getElementById('accessibility-panel');
    const close = document.getElementById('accessibility-close');
    const reset = document.getElementById('accessibility-reset');

    toggle.addEventListener('click', () => this.togglePanel());
    close.addEventListener('click', () => this.closePanel());
    reset.addEventListener('click', () => this.resetSettings());

    // Button controls
    panel.querySelectorAll('button[data-setting]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const setting = e.target.dataset.setting;
        const value = e.target.dataset.value;
        this.updateSetting(setting, value);

        // Update active state for button groups
        const group = e.target.parentElement;
        group.querySelectorAll('button').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
      });
    });

    // Checkbox controls
    panel.querySelectorAll('input[type="checkbox"][data-setting]').forEach(checkbox => {
      checkbox.addEventListener('change', (e) => {
        const setting = e.target.dataset.setting;
        this.updateSetting(setting, e.target.checked);
      });
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && panel.getAttribute('aria-hidden') === 'false') {
        this.closePanel();
      }
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (panel.getAttribute('aria-hidden') === 'false' &&
          !panel.contains(e.target) &&
          !toggle.contains(e.target)) {
        this.closePanel();
      }
    });
  }

  togglePanel() {
    const panel = document.getElementById('accessibility-panel');
    const toggle = document.getElementById('accessibility-toggle');
    const isHidden = panel.getAttribute('aria-hidden') === 'true';

    panel.setAttribute('aria-hidden', !isHidden);
    toggle.setAttribute('aria-expanded', isHidden);
    panel.classList.toggle('open');

    if (isHidden) {
      // Focus first interactive element
      const firstButton = panel.querySelector('button');
      if (firstButton) firstButton.focus();
    }
  }

  closePanel() {
    const panel = document.getElementById('accessibility-panel');
    const toggle = document.getElementById('accessibility-toggle');

    panel.setAttribute('aria-hidden', 'true');
    toggle.setAttribute('aria-expanded', 'false');
    panel.classList.remove('open');
    toggle.focus();
  }

  updateSetting(setting, value) {
    this.settings[setting] = value;
    this.saveSettings();
    this.applySettings();
  }

applySettings() {
    const html = document.documentElement;

    // Remove all accessibility classes
    html.classList.remove(
      'a11y-font-small', 'a11y-font-large', 'a11y-font-xlarge',
      'a11y-line-height-comfortable', 'a11y-line-height-spacious',
      'a11y-letter-spacing-light', 'a11y-letter-spacing-moderate', 'a11y-letter-spacing-heavy',
      'a11y-saturation-reduced', 'a11y-saturation-grayscale',
      'a11y-dyslexic-font', 'a11y-highlight-links'
    );

    // Apply font size
    if (this.settings.fontSize !== 'normal') {
      html.classList.add(`a11y-font-${this.settings.fontSize}`);
    }

    // Apply line height
    if (this.settings.lineHeight !== 'normal') {
      html.classList.add(`a11y-line-height-${this.settings.lineHeight}`);
    }

    // Apply letter spacing
    if (this.settings.letterSpacing !== 'normal') {
      html.classList.add(`a11y-letter-spacing-${this.settings.letterSpacing}`);
    }

    // Apply saturation
    if (this.settings.saturation !== 'normal') {
      html.classList.add(`a11y-saturation-${this.settings.saturation}`);
    }

    // Apply boolean settings
    if (this.settings.dyslexicFont) html.classList.add('a11y-dyslexic-font');
    if (this.settings.highlightLinks) html.classList.add('a11y-highlight-links');

    // Update checkbox states
    document.querySelectorAll('input[type="checkbox"][data-setting]').forEach(checkbox => {
      const setting = checkbox.dataset.setting;
      checkbox.checked = this.settings[setting];
    });

    // Update button active states
    document.querySelectorAll('button[data-setting]').forEach(btn => {
      const setting = btn.dataset.setting;
      const value = btn.dataset.value;
      if (this.settings[setting] === value) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  resetSettings() {
    if (confirm('Reset all accessibility settings to defaults?')) {
      this.settings = {
        fontSize: 'normal',
        lineHeight: 'normal',
        letterSpacing: 'normal',
        saturation: 'normal',
        dyslexicFont: false,
        highlightLinks: false
      };
      this.saveSettings();
      this.applySettings();
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new AccessibilityWidget();
  });
} else {
  new AccessibilityWidget();
}
