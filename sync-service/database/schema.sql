-- PostgreSQL Database Schema for Government Portal Sync Service
-- Created: 2025-12-04

-- Create database (run as postgres user)
-- CREATE DATABASE gov_portal_sync;

-- Connect to database
\c gov_portal_sync;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main sync data table
CREATE TABLE IF NOT EXISTS sync_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    folder_name VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    mime_type VARCHAR(100),
    data JSONB NOT NULL,
    html_output TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'processing', 'error', 'deleted')),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_file_per_folder UNIQUE(folder_name, file_id)
);

-- Index for faster lookups
CREATE INDEX idx_folder_name ON sync_data(folder_name);
CREATE INDEX idx_file_id ON sync_data(file_id);
CREATE INDEX idx_status ON sync_data(status);
CREATE INDEX idx_last_updated ON sync_data(last_updated DESC);

-- Sync log table for detailed tracking
CREATE TABLE IF NOT EXISTS sync_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation VARCHAR(50) NOT NULL,
    folder_name VARCHAR(255),
    file_name VARCHAR(255),
    file_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    message TEXT,
    error_details TEXT,
    duration_ms INTEGER,
    FOREIGN KEY (file_id) REFERENCES sync_data(file_id) ON DELETE SET NULL
);

-- Index for log queries
CREATE INDEX idx_sync_log_timestamp ON sync_log(timestamp DESC);
CREATE INDEX idx_sync_log_status ON sync_log(status);
CREATE INDEX idx_sync_log_operation ON sync_log(operation);

-- Folder configuration table
CREATE TABLE IF NOT EXISTS folder_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    folder_name VARCHAR(255) UNIQUE NOT NULL,
    drive_folder_id VARCHAR(255) UNIQUE NOT NULL,
    html_template VARCHAR(50) DEFAULT 'card',
    enabled BOOLEAN DEFAULT TRUE,
    last_check TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert default folder configurations (matching the government portal structure)
INSERT INTO folder_config (folder_name, drive_folder_id, html_template) VALUES
    ('meeting_agendas', '', 'document_card'),
    ('meeting_minutes', '', 'document_card'),
    ('meeting_packets', '', 'document_card'),
    ('meeting_recordings', '', 'video_card'),
    ('budgets', '', 'document_card'),
    ('financial_reports', '', 'document_card'),
    ('ordinances', '', 'document_card'),
    ('resolutions', '', 'document_card'),
    ('public_notices', '', 'notice_card'),
    ('event_flyers', '', 'event_card'),
    ('job_postings', '', 'job_card'),
    ('news_press_releases', '', 'news_card'),
    ('boards_commissions', '', 'document_card')
ON CONFLICT (folder_name) DO NOTHING;

-- Function to update last_updated timestamp
CREATE OR REPLACE FUNCTION update_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update last_updated
CREATE TRIGGER update_sync_data_timestamp
    BEFORE UPDATE ON sync_data
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated();

-- View for active files only
CREATE OR REPLACE VIEW active_files AS
SELECT
    folder_name,
    file_name,
    data,
    html_output,
    last_updated,
    mime_type
FROM sync_data
WHERE status = 'active'
ORDER BY folder_name, last_updated DESC;

-- View for error monitoring
CREATE OR REPLACE VIEW error_files AS
SELECT
    folder_name,
    file_name,
    error_message,
    retry_count,
    last_updated
FROM sync_data
WHERE status = 'error'
ORDER BY last_updated DESC;

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON DATABASE gov_portal_sync TO sync_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sync_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sync_user;

-- Sample query to check sync status
-- SELECT folder_name, COUNT(*) as file_count, MAX(last_updated) as last_sync
-- FROM sync_data
-- WHERE status = 'active'
-- GROUP BY folder_name
-- ORDER BY folder_name;
