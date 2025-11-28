/**
 * Component Loader - Loads header and footer components
 * Components are embedded to work with file:// protocol (no fetch needed)
 */

class ComponentLoader {
  constructor() {
    this.isHomePage = window.location.pathname.endsWith('index.html') ||
                      window.location.pathname.endsWith('/') ||
                      window.location.pathname === '/install/' ||
                      !window.location.pathname.includes('/pages/');
    this.basePath = this.isHomePage ? '' : '../';
    this.init();
  }

  init() {
    this.loadHeader();
    this.loadFooter();
  }

  loadHeader() {
    const headerElement = document.getElementById('header');
    if (!headerElement) return;

    const html = this.isHomePage ? this.getHomeHeader() : this.getPageHeader();
    headerElement.innerHTML = html;
  }

  loadFooter() {
    const footerElement = document.getElementById('footer');
    if (!footerElement) return;

    let html = this.getFooter();
    footerElement.innerHTML = html;

    // Load accessibility script (innerHTML doesn't execute scripts, so we add it manually)
    this.loadAccessibilityScript();
  }

  loadAccessibilityScript() {
    // Check if already loaded
    if (document.getElementById('accessibility-script')) return;

    const script = document.createElement('script');
    script.id = 'accessibility-script';
    script.src = `${this.basePath}assets/js/accessibility.js`;
    document.body.appendChild(script);
  }

  getHomeHeader() {
    return `<!-- Skip to Main Content Link for Accessibility -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Combined Banner with Navigation -->
<div class="combined-banner">
    <div class="banner-content">
        <h1 class="site-title">City Government Portal</h1>
        <p class="site-tagline">Accessible Services for All Citizens</p>
        <div class="main-navigation" role="navigation" aria-label="Main navigation">
            <button onclick="window.location.href='index.html'" aria-current="page">Home</button>
            <button onclick="window.location.href='pages/accessibility.html'">Accessibility</button>
            <button onclick="window.location.href='pages/contact.html'">Contact Us</button>
            <button onclick="window.location.href='pages/permits.html'">Permits</button>
            <button onclick="window.location.href='pages/pay-bills.html'">Pay Bills</button>
            <button onclick="window.location.href='pages/report-issue.html'">Report Issue</button>
            <button onclick="window.location.href='pages/public-records.html'">Public Records</button>
            <button onclick="window.location.href='pages/events.html'">Events</button>
            <button onclick="window.location.href='pages/council-meetings.html'">City Council</button>
            <button onclick="window.location.href='pages/staff-directory.html'">Staff Directory</button>
        </div>
    </div>
</div>`;
  }

  getPageHeader() {
    return `<!-- Skip to Main Content Link for Accessibility -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Combined Banner with Navigation -->
<div class="combined-banner">
    <div class="banner-content">
        <h1 class="site-title">City Government Portal</h1>
        <p class="site-tagline">Accessible Services for All Citizens</p>
        <div class="main-navigation" role="navigation" aria-label="Main navigation">
            <button onclick="window.location.href='../index.html'">Home</button>
            <button onclick="window.location.href='accessibility.html'">Accessibility</button>
            <button onclick="window.location.href='contact.html'">Contact Us</button>
            <button onclick="window.location.href='permits.html'">Permits</button>
            <button onclick="window.location.href='pay-bills.html'">Pay Bills</button>
            <button onclick="window.location.href='report-issue.html'">Report Issue</button>
            <button onclick="window.location.href='public-records.html'">Public Records</button>
            <button onclick="window.location.href='events.html'">Events</button>
            <button onclick="window.location.href='council-meetings.html'">City Council</button>
            <button onclick="window.location.href='staff-directory.html'">Staff Directory</button>
        </div>
    </div>
</div>`;
  }

  getFooter() {
    return `<footer role="contentinfo">
    <div class="footer-container">
        <div class="footer-grid">
            <div class="footer-section">
                <h3>Contact Information</h3>
                <ul>
                    <li>City Hall: <a href="tel:" data-contact="phone">ENTER_MAIN_PHONE_NUMBER_HERE</a></li>
                    <li>Email: <a href="mailto:" data-contact="email">ENTER_MAIN_EMAIL_HERE</a></li>
                    <li>Address: <span data-contact="address">ENTER_CITY_HALL_ADDRESS_HERE</span>, <span data-contact="address_line2">ENTER_CITY_STATE_ZIP_HERE</span></li>
                    <li>Hours: <span data-contact="hours">ENTER_OFFICE_HOURS_HERE</span></li>
                </ul>
            </div>
            <div class="footer-section">
                <h3>Quick Links</h3>
                <ul>
                    <li><a href="pages/accessibility.html" class="footer-link-accessibility">Accessibility</a></li>
                    <li><a href="pages/contact.html" class="footer-link-contact">Contact Us</a></li>
                    <li><a href="pages/faqs.html" class="footer-link-faqs">FAQs</a></li>
                    <li><a href="pages/careers.html" class="footer-link-careers">Careers</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h3>Services</h3>
                <ul>
                    <li><a href="pages/permits.html" class="footer-link-permits">Permits</a></li>
                    <li><a href="pages/pay-bills.html" class="footer-link-pay-bills">Pay Bills</a></li>
                    <li><a href="pages/report-issue.html" class="footer-link-report-issue">Report Issue</a></li>
                    <li><a href="pages/public-records.html" class="footer-link-public-records">Public Records</a></li>
                </ul>
            </div>
            <div class="footer-section">
                <h3>Government</h3>
                <ul>
                    <li><a href="pages/council-meetings.html" class="footer-link-council-meetings">City Council</a></li>
                    <li><a href="pages/staff-directory.html" class="footer-link-staff-directory">Staff Directory</a></li>
                    <li><a href="pages/news.html" class="footer-link-news">News</a></li>
                    <li><a href="pages/forms.html" class="footer-link-forms">Forms</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 City Government. All rights reserved. | <a href="pages/accessibility.html" class="footer-link-accessibility-statement">Accessibility Statement</a></p>
        </div>
    </div>
</footer>`;
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
