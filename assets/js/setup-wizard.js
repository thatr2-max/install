/**
 * Setup Wizard JavaScript
 * Handles the GUI configuration builder for user-setup.json
 */

// Google Drive folder names - matches user-setup.json structure
const GOOGLE_DRIVE_FOLDERS = [
    { key: 'meeting_agendas', label: 'Meeting Agendas' },
    { key: 'meeting_minutes', label: 'Meeting Minutes' },
    { key: 'meeting_packets', label: 'Meeting Packets' },
    { key: 'meeting_recordings', label: 'Meeting Recordings' },
    { key: 'voting_records', label: 'Voting Records' },
    { key: 'budgets', label: 'Budgets' },
    { key: 'financial_reports', label: 'Financial Reports' },
    { key: 'audit_reports', label: 'Audit Reports' },
    { key: 'ordinances', label: 'Ordinances' },
    { key: 'resolutions', label: 'Resolutions' },
    { key: 'municipal_codes', label: 'Municipal Codes' },
    { key: 'public_notices', label: 'Public Notices' },
    { key: 'rfps_bids', label: 'RFPs & Bids' },
    { key: 'zoning_maps', label: 'Zoning Maps' },
    { key: 'comprehensive_plans', label: 'Comprehensive Plans' },
    { key: 'building_permits_public', label: 'Building Permits (Public)' },
    { key: 'street_closures', label: 'Street Closures' },
    { key: 'construction_updates', label: 'Construction Updates' },
    { key: 'utility_interruptions', label: 'Utility Interruptions' },
    { key: 'event_flyers', label: 'Event Flyers' },
    { key: 'recreation_schedules', label: 'Recreation Schedules' },
    { key: 'newsletters', label: 'Newsletters' },
    { key: 'job_postings', label: 'Job Postings' },
    { key: 'emergency_alerts', label: 'Emergency Alerts' },
    { key: 'weather_advisories', label: 'Weather Advisories' },
    { key: 'events', label: 'Events' },
    { key: 'event_calendar', label: 'Event Calendar' },
    { key: 'news_press_releases', label: 'News & Press Releases' },
    { key: 'capital_projects', label: 'Capital Projects' },
    { key: 'parks_maps', label: 'Parks Maps' },
    { key: 'trails_maps', label: 'Trails Maps' }
];

let councilMemberCount = 0;

// Initialize the wizard when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeGoogleDriveFolders();
    addCouncilMember('Mayor', '', true); // Add mayor by default
    addCouncilMember('Council Member', 'District 1', false); // Add one council member
});

/**
 * Initialize Google Drive folder input fields
 */
function initializeGoogleDriveFolders() {
    const container = document.getElementById('google-drive-folders');
    if (!container) return;

    GOOGLE_DRIVE_FOLDERS.forEach(folder => {
        const field = document.createElement('div');
        field.className = 'form-field';
        field.innerHTML = `
            <label for="folder-${folder.key}">${folder.label}</label>
            <input type="text" id="folder-${folder.key}"
                   placeholder="Folder ID (optional)"
                   data-folder-key="${folder.key}">
            <small>Leave blank if not using</small>
        `;
        container.appendChild(field);
    });
}

/**
 * Add a new council member card
 */
function addCouncilMember(defaultPosition = 'Council Member', defaultDistrict = '', isMayor = false) {
    const container = document.getElementById('council-members-container');
    if (!container) return;

    const memberDiv = document.createElement('div');
    memberDiv.className = 'council-member-card';
    memberDiv.dataset.memberIndex = councilMemberCount;

    memberDiv.innerHTML = `
        <h4>${isMayor ? 'Mayor' : `Council Member ${councilMemberCount + 1}`}</h4>
        ${!isMayor ? `<button type="button" class="remove-member-btn" onclick="removeCouncilMember(${councilMemberCount})">Remove</button>` : ''}

        <div class="form-grid">
            <div class="form-field">
                <label for="member-name-${councilMemberCount}">Full Name *</label>
                <input type="text" id="member-name-${councilMemberCount}" required
                       placeholder="e.g., John Smith">
            </div>
            <div class="form-field">
                <label for="member-position-${councilMemberCount}">Position *</label>
                <input type="text" id="member-position-${councilMemberCount}" required
                       value="${defaultPosition}"
                       placeholder="e.g., Mayor or Council Member">
            </div>
            <div class="form-field">
                <label for="member-email-${councilMemberCount}">Email Address *</label>
                <input type="email" id="member-email-${councilMemberCount}" required
                       placeholder="e.g., mayor@citygovernment.gov">
            </div>
            <div class="form-field">
                <label for="member-phone-${councilMemberCount}">Phone Number *</label>
                <input type="tel" id="member-phone-${councilMemberCount}" required
                       placeholder="e.g., (555) 123-4500">
            </div>
            <div class="form-field">
                <label for="member-district-${councilMemberCount}">District (Optional)</label>
                <input type="text" id="member-district-${councilMemberCount}"
                       value="${defaultDistrict}"
                       placeholder="e.g., District 1">
            </div>
        </div>
    `;

    container.appendChild(memberDiv);
    councilMemberCount++;
}

/**
 * Remove a council member card
 */
function removeCouncilMember(index) {
    const memberCard = document.querySelector(`[data-member-index="${index}"]`);
    if (memberCard) {
        memberCard.remove();
    }
}

/**
 * Load existing configuration from file
 */
async function loadExistingConfig() {
    try {
        const response = await fetch('user-setup.json');
        if (!response.ok) {
            alert('Could not load existing configuration. Please fill in the form manually.');
            return;
        }

        const config = await response.json();

        // Load municipality info
        document.getElementById('municipality-name').value = config.municipality?.name || '';
        document.getElementById('banner-image').value = config.municipality?.banner_image || 'assets/images/banner.svg';
        document.getElementById('show-banner').checked = config.municipality?.show_banner !== false;

        // Load contact info
        document.getElementById('city-hall-address').value = config.contact_info?.city_hall_address || '';
        document.getElementById('city-hall-address-line2').value = config.contact_info?.city_hall_address_line2 || '';
        document.getElementById('main-phone').value = config.contact_info?.main_phone || '';
        document.getElementById('main-email').value = config.contact_info?.main_email || '';
        document.getElementById('office-hours').value = config.contact_info?.office_hours || '';

        // Load form email
        document.getElementById('form-email').value = config.form_submissions?.default_email || '';

        // Load Google Drive config
        document.getElementById('google-api-key').value = config.google_drive?.api_key || '';
        document.getElementById('google-drive-enabled').checked = config.google_drive?.enabled !== false;

        // Load Google Drive folders
        if (config.google_drive?.folders) {
            Object.keys(config.google_drive.folders).forEach(key => {
                const input = document.getElementById(`folder-${key}`);
                if (input) {
                    input.value = config.google_drive.folders[key] || '';
                }
            });
        }

        // Load council members
        if (config.council_members && config.council_members.length > 0) {
            // Clear existing members
            document.getElementById('council-members-container').innerHTML = '';
            councilMemberCount = 0;

            // Add each member from config
            config.council_members.forEach((member, index) => {
                const isMayor = member.position.toLowerCase().includes('mayor');
                addCouncilMember(member.position, member.district || '', isMayor);

                // Populate fields
                document.getElementById(`member-name-${index}`).value = member.name || '';
                document.getElementById(`member-position-${index}`).value = member.position || '';
                document.getElementById(`member-email-${index}`).value = member.email || '';
                document.getElementById(`member-phone-${index}`).value = member.phone || '';
                document.getElementById(`member-district-${index}`).value = member.district || '';
            });
        }

        alert('✅ Configuration loaded successfully! Review and modify as needed.');

    } catch (error) {
        console.error('Error loading configuration:', error);
        alert('Error loading configuration file. Please fill in the form manually.');
    }
}

/**
 * Generate configuration object from form data
 */
function generateConfig() {
    // Validate form
    const form = document.getElementById('setup-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Build council members array
    const councilMembers = [];
    const memberCards = document.querySelectorAll('.council-member-card');
    memberCards.forEach((card, index) => {
        const idx = card.dataset.memberIndex;
        const name = document.getElementById(`member-name-${idx}`)?.value || '';
        const position = document.getElementById(`member-position-${idx}`)?.value || '';
        const email = document.getElementById(`member-email-${idx}`)?.value || '';
        const phone = document.getElementById(`member-phone-${idx}`)?.value || '';
        const district = document.getElementById(`member-district-${idx}`)?.value || '';

        if (name && position && email && phone) {
            councilMembers.push({
                name,
                position,
                email,
                phone,
                district
            });
        }
    });

    // Build Google Drive folders object
    const folders = {};
    GOOGLE_DRIVE_FOLDERS.forEach(folder => {
        const input = document.getElementById(`folder-${folder.key}`);
        if (input) {
            folders[folder.key] = input.value || '';
        }
    });

    // Build complete configuration
    const config = {
        municipality: {
            name: document.getElementById('municipality-name').value,
            banner_image: document.getElementById('banner-image').value,
            show_banner: document.getElementById('show-banner').checked
        },
        contact_info: {
            city_hall_address: document.getElementById('city-hall-address').value,
            city_hall_address_line2: document.getElementById('city-hall-address-line2').value,
            main_phone: document.getElementById('main-phone').value,
            main_email: document.getElementById('main-email').value,
            office_hours: document.getElementById('office-hours').value,
            note: "Fill in your municipality's contact information"
        },
        council_members: councilMembers,
        form_submissions: {
            default_email: document.getElementById('form-email').value,
            note: "Change default_email to the address where ALL forms should be sent"
        },
        google_drive: {
            api_key: document.getElementById('google-api-key').value || 'YOUR_GOOGLE_API_KEY_HERE',
            enabled: document.getElementById('google-drive-enabled').checked,
            folders: folders,
            note: "Get API key from https://console.cloud.google.com/ - Instructions in GOOGLE_DRIVE_SETUP.md"
        },
        quick_actions: {
            permits: true,
            pay_bills: true,
            report_issue: true,
            public_records: true
        },
        homepage_cards: {
            permits_licenses: true,
            pay_bills_taxes: true,
            report_issue: true,
            public_records: true,
            community_events: true,
            staff_directory: true,
            careers: true,
            city_council: true,
            public_services: true,
            parks_recreation: true,
            emergency_management: true,
            news_updates: true
        }
    };

    // Download the file
    downloadConfig(config);

    // Show success message
    const successMsg = document.getElementById('success-message');
    successMsg.style.display = 'block';
    successMsg.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Download configuration as JSON file
 */
function downloadConfig(config) {
    const jsonString = JSON.stringify(config, null, 2);
    const blob = new Blob([jsonString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = 'user-setup.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Copy configuration to clipboard
 */
function copyToClipboard() {
    // Validate form
    const form = document.getElementById('setup-form');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Generate config (reuse the same logic)
    const councilMembers = [];
    const memberCards = document.querySelectorAll('.council-member-card');
    memberCards.forEach((card) => {
        const idx = card.dataset.memberIndex;
        const name = document.getElementById(`member-name-${idx}`)?.value || '';
        const position = document.getElementById(`member-position-${idx}`)?.value || '';
        const email = document.getElementById(`member-email-${idx}`)?.value || '';
        const phone = document.getElementById(`member-phone-${idx}`)?.value || '';
        const district = document.getElementById(`member-district-${idx}`)?.value || '';

        if (name && position && email && phone) {
            councilMembers.push({ name, position, email, phone, district });
        }
    });

    const folders = {};
    GOOGLE_DRIVE_FOLDERS.forEach(folder => {
        const input = document.getElementById(`folder-${folder.key}`);
        if (input) {
            folders[folder.key] = input.value || '';
        }
    });

    const config = {
        municipality: {
            name: document.getElementById('municipality-name').value,
            banner_image: document.getElementById('banner-image').value,
            show_banner: document.getElementById('show-banner').checked
        },
        contact_info: {
            city_hall_address: document.getElementById('city-hall-address').value,
            city_hall_address_line2: document.getElementById('city-hall-address-line2').value,
            main_phone: document.getElementById('main-phone').value,
            main_email: document.getElementById('main-email').value,
            office_hours: document.getElementById('office-hours').value,
            note: "Fill in your municipality's contact information"
        },
        council_members: councilMembers,
        form_submissions: {
            default_email: document.getElementById('form-email').value,
            note: "Change default_email to the address where ALL forms should be sent"
        },
        google_drive: {
            api_key: document.getElementById('google-api-key').value || 'YOUR_GOOGLE_API_KEY_HERE',
            enabled: document.getElementById('google-drive-enabled').checked,
            folders: folders,
            note: "Get API key from https://console.cloud.google.com/ - Instructions in GOOGLE_DRIVE_SETUP.md"
        },
        quick_actions: {
            permits: true,
            pay_bills: true,
            report_issue: true,
            public_records: true
        },
        homepage_cards: {
            permits_licenses: true,
            pay_bills_taxes: true,
            report_issue: true,
            public_records: true,
            community_events: true,
            staff_directory: true,
            careers: true,
            city_council: true,
            public_services: true,
            parks_recreation: true,
            emergency_management: true,
            news_updates: true
        }
    };

    const jsonString = JSON.stringify(config, null, 2);

    // Copy to clipboard
    navigator.clipboard.writeText(jsonString).then(() => {
        alert('✅ Configuration copied to clipboard! Paste it into user-setup.json file.');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('❌ Failed to copy to clipboard. Please use the Download button instead.');
    });
}
