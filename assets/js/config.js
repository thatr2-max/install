/**
 * Municipality Configuration
 *
 * This file contains all municipality-specific data that is loaded
 * dynamically across the site. Edit these values to customize your
 * government portal.
 */

const MunicipalityConfig = {
    // Basic Information
    municipality_name: "City of Springfield",
    municipality_type: "City", // City, Town, Village, etc.
    state: "State",

    // Contact Information
    clerk_name: "Jane Smith",
    clerk_phone: "222-222-2222",
    clerk_email: "clerk@springfield.gov",
    clerk_fax: "222-222-2223",

    main_phone: "222-222-2200",
    main_email: "info@springfield.gov",

    // Address
    street_address: "123 Main Street",
    city: "Springfield",
    state_abbr: "ST",
    zip_code: "12345",

    // Hours
    office_hours: "Monday - Friday: 8:00 AM - 4:30 PM",

    // Social Media
    facebook_url: "",
    twitter_url: "",
    instagram_url: "",

    // Department Heads
    mayor_name: "John Doe",
    mayor_email: "mayor@springfield.gov",
    mayor_phone: "222-222-2201",

    administrator_name: "",
    administrator_email: "",
    administrator_phone: "",

    police_chief_name: "",
    police_phone: "911",
    police_non_emergency: "222-222-2300",

    fire_chief_name: "",
    fire_phone: "911",
    fire_non_emergency: "222-222-2400",

    public_works_director: "",
    public_works_phone: "222-222-2500",

    // Utility Information
    water_department_phone: "",
    sewer_department_phone: "",

    // Meeting Information
    council_meeting_day: "First and Third Tuesday",
    council_meeting_time: "7:00 PM",
    council_meeting_location: "City Hall Council Chambers",

    // Financial
    tax_collector_name: "",
    tax_collector_phone: "",
    tax_collector_email: "",

    // Emergency Alerts
    emergency_alert_text: "",
    emergency_alert_link: "",

    // Google Drive Folder IDs (for sync service)
    google_drive_folders: {
        meeting_agendas: "",
        meeting_minutes: "",
        meeting_packets: "",
        meeting_recordings: "",
        budgets: "",
        financial_reports: "",
        ordinances: "",
        resolutions: "",
        public_notices: "",
        event_flyers: "",
        job_postings: "",
        news_press_releases: "",
        boards_commissions: "",
        events: "",
        event_calendar: "",
        capital_projects: ""
    },

    // Google Sheets IDs (for data sources)
    google_sheets: {
        staff_directory: "",
        departments: "",
        events: "",
        public_notices: "",
        boards_commissions: "",
        job_postings: "",
        news: ""
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MunicipalityConfig;
}
