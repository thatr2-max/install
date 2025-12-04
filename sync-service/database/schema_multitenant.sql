-- Multi-Tenant PostgreSQL Database Schema for Government Portal Sync Service
-- Updated: 2025-12-04

-- Create database (run as postgres user)
-- CREATE DATABASE gov_portal_sync;

-- Connect to database
\c gov_portal_sync;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tenants/Municipalities table
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_key VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'springfield', 'riverside'
    name VARCHAR(255) NOT NULL,  -- e.g., 'Springfield City Government'
    domain VARCHAR(255),  -- e.g., 'springfield.gov'
    output_path VARCHAR(500) NOT NULL,  -- Where to output HTML files
    google_service_account_file VARCHAR(500),  -- Path to service account JSON
    sync_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb  -- Store additional config
);

-- Index for tenant lookups
CREATE INDEX idx_tenant_key ON tenants(tenant_key);
CREATE INDEX idx_tenant_sync_enabled ON tenants(sync_enabled);

-- Main sync data table (now with tenant_id)
CREATE TABLE IF NOT EXISTS sync_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    folder_name VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_id VARCHAR(255) NOT NULL,
    mime_type VARCHAR(100),
    data JSONB NOT NULL,
    html_output TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'processing', 'error', 'deleted')),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_file_per_tenant_folder UNIQUE(tenant_id, folder_name, file_id)
);

-- Index for faster lookups
CREATE INDEX idx_sync_data_tenant_id ON sync_data(tenant_id);
CREATE INDEX idx_sync_data_folder_name ON sync_data(tenant_id, folder_name);
CREATE INDEX idx_sync_data_file_id ON sync_data(file_id);
CREATE INDEX idx_sync_data_status ON sync_data(tenant_id, status);
CREATE INDEX idx_sync_data_last_updated ON sync_data(tenant_id, last_updated DESC);

-- Sync log table (now with tenant_id)
CREATE TABLE IF NOT EXISTS sync_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation VARCHAR(50) NOT NULL,
    folder_name VARCHAR(255),
    file_name VARCHAR(255),
    file_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    message TEXT,
    error_details TEXT,
    duration_ms INTEGER
);

-- Index for log queries
CREATE INDEX idx_sync_log_tenant_id ON sync_log(tenant_id);
CREATE INDEX idx_sync_log_timestamp ON sync_log(timestamp DESC);
CREATE INDEX idx_sync_log_status ON sync_log(tenant_id, status);
CREATE INDEX idx_sync_log_operation ON sync_log(tenant_id, operation);

-- Folder configuration table (now per tenant)
CREATE TABLE IF NOT EXISTS folder_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    folder_name VARCHAR(255) NOT NULL,
    drive_folder_id VARCHAR(255) NOT NULL,
    html_template VARCHAR(50) DEFAULT 'card',
    enabled BOOLEAN DEFAULT TRUE,
    last_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_folder_per_tenant UNIQUE(tenant_id, folder_name)
);

-- Index for folder config
CREATE INDEX idx_folder_config_tenant_id ON folder_config(tenant_id);
CREATE INDEX idx_folder_config_enabled ON folder_config(tenant_id, enabled);

-- Function to initialize folders for a new tenant
CREATE OR REPLACE FUNCTION initialize_tenant_folders(p_tenant_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Insert default folder configurations for the new tenant
    INSERT INTO folder_config (tenant_id, folder_name, drive_folder_id, html_template)
    VALUES
        (p_tenant_id, 'meeting_agendas', '', 'document_card'),
        (p_tenant_id, 'meeting_minutes', '', 'document_card'),
        (p_tenant_id, 'meeting_packets', '', 'document_card'),
        (p_tenant_id, 'meeting_recordings', '', 'video_card'),
        (p_tenant_id, 'budgets', '', 'document_card'),
        (p_tenant_id, 'financial_reports', '', 'document_card'),
        (p_tenant_id, 'ordinances', '', 'document_card'),
        (p_tenant_id, 'resolutions', '', 'document_card'),
        (p_tenant_id, 'public_notices', '', 'notice_card'),
        (p_tenant_id, 'event_flyers', '', 'event_card'),
        (p_tenant_id, 'job_postings', '', 'job_card'),
        (p_tenant_id, 'news_press_releases', '', 'news_card'),
        (p_tenant_id, 'boards_commissions', '', 'document_card')
    ON CONFLICT (tenant_id, folder_name) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update last_updated
DROP TRIGGER IF EXISTS update_sync_data_timestamp ON sync_data;
CREATE TRIGGER update_sync_data_timestamp
    BEFORE UPDATE ON sync_data
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();

-- View for active files per tenant
CREATE OR REPLACE VIEW active_files_by_tenant AS
SELECT
    t.tenant_key,
    t.name as tenant_name,
    sd.folder_name,
    sd.file_name,
    sd.data,
    sd.html_output,
    sd.last_updated,
    sd.mime_type
FROM sync_data sd
JOIN tenants t ON sd.tenant_id = t.id
WHERE sd.status = 'active'
ORDER BY t.tenant_key, sd.folder_name, sd.last_updated DESC;

-- View for error monitoring per tenant
CREATE OR REPLACE VIEW error_files_by_tenant AS
SELECT
    t.tenant_key,
    t.name as tenant_name,
    sd.folder_name,
    sd.file_name,
    sd.error_message,
    sd.retry_count,
    sd.last_updated
FROM sync_data sd
JOIN tenants t ON sd.tenant_id = t.id
WHERE sd.status = 'error'
ORDER BY t.tenant_key, sd.last_updated DESC;

-- View for tenant sync status
CREATE OR REPLACE VIEW tenant_sync_status AS
SELECT
    t.tenant_key,
    t.name,
    t.sync_enabled,
    COUNT(sd.id) as total_files,
    SUM(CASE WHEN sd.status = 'active' THEN 1 ELSE 0 END) as active_files,
    SUM(CASE WHEN sd.status = 'error' THEN 1 ELSE 0 END) as error_files,
    MAX(sd.last_synced) as last_sync
FROM tenants t
LEFT JOIN sync_data sd ON t.id = sd.tenant_id
GROUP BY t.id, t.tenant_key, t.name, t.sync_enabled
ORDER BY t.tenant_key;

-- Sample: Add your first tenant
-- INSERT INTO tenants (tenant_key, name, domain, output_path, google_service_account_file)
-- VALUES (
--     'springfield',
--     'Springfield City Government',
--     'springfield.gov',
--     '/var/www/springfield/pages/generated',
--     '/home/user/install/sync-service/credentials/springfield-service-account.json'
-- )
-- RETURNING id;

-- Then initialize folders for that tenant (use the returned ID)
-- SELECT initialize_tenant_folders('TENANT_UUID_HERE');

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON DATABASE gov_portal_sync TO sync_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sync_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sync_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sync_user;

-- Sample queries for multi-tenant monitoring
--
-- View all tenants:
-- SELECT * FROM tenant_sync_status;
--
-- View files for specific tenant:
-- SELECT * FROM active_files_by_tenant WHERE tenant_key = 'springfield';
--
-- View sync status per tenant and folder:
-- SELECT t.tenant_key, sd.folder_name, COUNT(*) as file_count, MAX(sd.last_updated) as last_sync
-- FROM sync_data sd
-- JOIN tenants t ON sd.tenant_id = t.id
-- WHERE sd.status = 'active'
-- GROUP BY t.tenant_key, sd.folder_name
-- ORDER BY t.tenant_key, sd.folder_name;
