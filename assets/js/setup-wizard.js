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

let formEmailCount = 0;

// All available forms that can receive submissions
const ALL_FORMS = [
    'accessibility.html',
    'animal-control.html',
    'building-inspections.html',
    'business-licenses.html',
    'city-council.html',
    'code-enforcement.html',
    'contact.html',
    'council-meetings.html',
    'emergency-management.html',
    'events.html',
    'garbage-recycling.html',
    'municipal-court.html',
    'news.html',
    'open-data.html',
    'pay-bills.html',
    'permits.html',
    'planning-zoning.html',
    'public-records.html',
    'public-safety.html',
    'report-issue.html',
    'staff-directory.html',
    'street-maintenance.html',
    'tax-information.html',
    'volunteer.html',
    'voting-elections.html',
    'weather-alerts.html'
];

// Initialize the wizard when page loads
document.addEventListener('DOMContentLoaded', () => {
    initializeGoogleDriveFolders();
    addCouncilMember('Mayor', '', true); // Add mayor by default
    addCouncilMember('Council Member', 'District 1', false); // Add one council member
    addFormEmail(); // Add first email address by default
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
 * Add a new form email configuration card
 */
function addFormEmail() {
    const container = document.getElementById('form-emails-container');
    if (!container) return;

    // Check if we already have 10 emails
    const emailCards = document.querySelectorAll('.form-email-card');
    if (emailCards.length >= 10) {
        alert('Maximum of 10 email addresses allowed');
        return;
    }

    const emailDiv = document.createElement('div');
    emailDiv.className = 'form-email-card council-member-card';
    emailDiv.dataset.emailIndex = formEmailCount;

    // Get already assigned forms
    const assignedForms = getAssignedForms();
    const availableForms = ALL_FORMS.filter(form => !assignedForms.includes(form));

    // If this is the first email, select all forms by default
    const isFirstEmail = emailCards.length === 0;

    emailDiv.innerHTML = `
        <h4>Email Address ${formEmailCount + 1}</h4>
        ${formEmailCount > 0 ? `<button type="button" class="remove-member-btn" onclick="removeFormEmail(${formEmailCount})">Remove</button>` : ''}

        <div class="form-grid">
            <div class="form-field">
                <label for="email-address-${formEmailCount}">Email Address *</label>
                <input type="email" id="email-address-${formEmailCount}" required
                       placeholder="e.g., admin@citygovernment.gov"
                       onchange="updateFormAssignments()">
            </div>
            <div class="form-field">
                <label for="email-label-${formEmailCount}">Label/Description</label>
                <input type="text" id="email-label-${formEmailCount}"
                       placeholder="e.g., Main Admin, Permits Dept">
                <small>Optional - helps you identify this email</small>
            </div>
        </div>

        <div class="form-field" style="margin-top: 1rem;">
            <label>Assigned Forms (${isFirstEmail ? ALL_FORMS.length : availableForms.length} selected)</label>
            <div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 1rem; border-radius: 4px; background: #f8f9fa;">
                <label style="font-weight: bold; display: block; margin-bottom: 0.5rem;">
                    <input type="checkbox" onchange="toggleAllForms(${formEmailCount}, this.checked)" ${isFirstEmail ? 'checked' : ''}>
                    Select All
                </label>
                <hr style="margin: 0.5rem 0;">
                ${generateFormCheckboxes(formEmailCount, isFirstEmail ? ALL_FORMS : availableForms, isFirstEmail)}
            </div>
            <small>Select which forms should send to this email address</small>
        </div>
    `;

    container.appendChild(emailDiv);
    formEmailCount++;
}

/**
 * Generate form checkboxes
 */
function generateFormCheckboxes(emailIndex, availableForms, selectAll = false) {
    return ALL_FORMS.map(form => {
        const disabled = !availableForms.includes(form);
        const checked = selectAll && !disabled;
        const formName = form.replace('.html', '').replace(/-/g, ' ')
            .split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

        return `
            <label style="display: block; margin: 0.25rem 0; ${disabled ? 'opacity: 0.5;' : ''}">
                <input type="checkbox"
                       class="form-checkbox-${emailIndex}"
                       data-form="${form}"
                       data-email-index="${emailIndex}"
                       ${checked ? 'checked' : ''}
                       ${disabled ? 'disabled' : ''}
                       onchange="updateFormAssignments()">
                ${formName} ${disabled ? '(already assigned)' : ''}
            </label>
        `;
    }).join('');
}

/**
 * Toggle all forms for an email
 */
function toggleAllForms(emailIndex, checked) {
    const checkboxes = document.querySelectorAll(`.form-checkbox-${emailIndex}:not(:disabled)`);
    checkboxes.forEach(cb => {
        cb.checked = checked;
    });
    updateFormAssignments();
}

/**
 * Get all currently assigned forms across all emails
 */
function getAssignedForms() {
    const assigned = [];
    const emailCards = document.querySelectorAll('.form-email-card');

    emailCards.forEach(card => {
        const emailIndex = card.dataset.emailIndex;
        const checkboxes = card.querySelectorAll(`input[type="checkbox"][data-form]:checked`);
        checkboxes.forEach(cb => {
            const form = cb.dataset.form;
            if (form && !assigned.includes(form)) {
                assigned.push(form);
            }
        });
    });

    return assigned;
}

/**
 * Update form assignments when checkboxes change
 */
function updateFormAssignments() {
    const assignedForms = getAssignedForms();
    const unassignedForms = ALL_FORMS.filter(f => !assignedForms.includes(f));

    // Update validation warning
    const warning = document.getElementById('email-validation-error');
    if (unassignedForms.length > 0) {
        warning.style.display = 'block';
        warning.innerHTML = `⚠️ Warning: ${unassignedForms.length} form(s) not assigned to any email: ${unassignedForms.map(f => f.replace('.html', '')).join(', ')}`;
    } else {
        warning.style.display = 'none';
    }

    // Refresh all email cards to update disabled states
    refreshFormCheckboxes();
}

/**
 * Refresh form checkboxes to show current assignments
 */
function refreshFormCheckboxes() {
    const emailCards = document.querySelectorAll('.form-email-card');
    const assignedForms = getAssignedForms();

    emailCards.forEach(card => {
        const emailIndex = card.dataset.emailIndex;
        const checkboxContainer = card.querySelector('div[style*="max-height"]');
        if (!checkboxContainer) return;

        // Get currently selected forms for this email
        const selectedForms = [];
        const checkboxes = card.querySelectorAll(`input[type="checkbox"][data-form]:checked`);
        checkboxes.forEach(cb => {
            if (cb.dataset.form) {
                selectedForms.push(cb.dataset.form);
            }
        });

        // Determine which forms are available for this email
        const availableForms = ALL_FORMS.filter(form =>
            selectedForms.includes(form) || !assignedForms.includes(form)
        );

        // Regenerate checkboxes
        const label = checkboxContainer.querySelector('label');
        const hr = checkboxContainer.querySelector('hr');
        const existingCheckboxes = checkboxContainer.querySelectorAll('label:not(:first-child)');
        existingCheckboxes.forEach(el => el.remove());

        const newCheckboxesHTML = generateFormCheckboxes(emailIndex, availableForms, false);
        checkboxContainer.insertAdjacentHTML('beforeend', newCheckboxesHTML);

        // Restore checked state
        selectedForms.forEach(form => {
            const checkbox = checkboxContainer.querySelector(`input[data-form="${form}"]`);
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    });
}

/**
 * Remove a form email configuration
 */
function removeFormEmail(index) {
    const emailCard = document.querySelector(`.form-email-card[data-email-index="${index}"]`);
    if (emailCard) {
        emailCard.remove();
        updateFormAssignments();
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

        // Load form emails
        if (config.form_emails && config.form_emails.length > 0) {
            // Clear existing emails
            document.getElementById('form-emails-container').innerHTML = '';
            formEmailCount = 0;

            // Add each email configuration
            config.form_emails.forEach((emailConfig, index) => {
                addFormEmail();
                const idx = formEmailCount - 1;

                // Populate fields
                document.getElementById(`email-address-${idx}`).value = emailConfig.email || '';
                document.getElementById(`email-label-${idx}`).value = emailConfig.label || '';

                // Select forms
                if (emailConfig.forms && emailConfig.forms.length > 0) {
                    emailConfig.forms.forEach(form => {
                        const checkbox = document.querySelector(`input[data-email-index="${idx}"][data-form="${form}"]`);
                        if (checkbox) {
                            checkbox.checked = true;
                        }
                    });
                }
            });

            updateFormAssignments();
        }

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

    // Build form emails array
    const formEmails = [];
    const emailCards = document.querySelectorAll('.form-email-card');
    emailCards.forEach(card => {
        const idx = card.dataset.emailIndex;
        const email = document.getElementById(`email-address-${idx}`)?.value || '';
        const label = document.getElementById(`email-label-${idx}`)?.value || '';

        if (email) {
            const forms = [];
            const checkboxes = card.querySelectorAll('input[type="checkbox"][data-form]:checked');
            checkboxes.forEach(cb => {
                if (cb.dataset.form) {
                    forms.push(cb.dataset.form);
                }
            });

            formEmails.push({
                email,
                label,
                forms
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
        form_emails: formEmails,
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
