# Government Portal Sync Service

Server-side sync service that monitors Google Drive folders, parses structured data, stores it in PostgreSQL, and auto-generates static HTML cards for the government portal.

## Features

- ✅ **Event-driven monitoring** of Google Drive folders using service account
- ✅ **Automatic file parsing** for spreadsheets, documents, PDFs, markdown, and videos
- ✅ **PostgreSQL storage** with full transaction support
- ✅ **Auto-generated HTML** cards matching existing portal design
- ✅ **Comprehensive logging** with timestamps, operations, and status tracking
- ✅ **Error handling** with automatic retry logic and exponential backoff
- ✅ **Systemd service** integration for continuous operation
- ✅ **Monitoring dashboard** for real-time status checks

## Architecture

```
Google Drive Folders
        ↓
   Sync Worker (Python)
        ↓
   File Parsers → PostgreSQL Database → HTML Generator
                                              ↓
                                     Static HTML Files
                                              ↓
                                      Government Portal
```

## Quick Start

1. **Prerequisites**: Python 3.10+, PostgreSQL 13+, Google service account

2. **Install**:
   ```bash
   cd sync-service
   python3.10 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Initialize Database**:
   ```bash
   sudo -u postgres psql -d gov_portal_sync -f database/schema.sql
   ```

5. **Run**:
   ```bash
   python sync_worker.py
   ```

## Directory Structure

```
sync-service/
├── config.py                 # Configuration settings
├── sync_worker.py           # Main sync service
├── monitor.py               # Monitoring dashboard
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── SETUP_INSTRUCTIONS.md   # Complete setup guide
├── database/
│   ├── schema.sql          # PostgreSQL schema
│   └── db_manager.py       # Database operations
├── parsers/
│   └── file_parser.py      # File type parsers
├── generators/
│   └── html_generator.py   # HTML card generator
├── credentials/
│   └── service-account.json # Google service account key
└── logs/
    ├── sync.log            # Application logs
    └── error.log           # Error logs
```

## Configuration

### Environment Variables

See `.env.example` for all configuration options.

Key settings:
- `DB_*`: PostgreSQL connection details
- `GOOGLE_SERVICE_ACCOUNT`: Path to service account JSON
- `SYNC_POLL_INTERVAL`: How often to check for changes (seconds)
- `MAX_RETRIES`: Maximum retry attempts for failed files

### Folder Configuration

Folder mappings are stored in PostgreSQL `folder_config` table:

```sql
SELECT folder_name, drive_folder_id, enabled FROM folder_config;
```

Update folder IDs:
```sql
UPDATE folder_config
SET drive_folder_id = 'YOUR_FOLDER_ID'
WHERE folder_name = 'meeting_agendas';
```

## Monitoring

### Dashboard

Run the monitoring dashboard:
```bash
python monitor.py
```

Shows:
- Sync status per folder
- File counts and errors
- Recent activity
- Log file status

### Logs

- **Application logs**: `logs/sync.log`
- **Error logs**: `logs/error.log`
- **System logs**: `sudo journalctl -u gov-portal-sync`

### Database Queries

Check sync status:
```sql
SELECT folder_name, COUNT(*) as files, MAX(last_updated) as last_sync
FROM sync_data
WHERE status = 'active'
GROUP BY folder_name;
```

View errors:
```sql
SELECT * FROM error_files;
```

Recent activity:
```sql
SELECT * FROM sync_log ORDER BY timestamp DESC LIMIT 20;
```

## Supported File Types

| Type | MIME Type | Features |
|------|-----------|----------|
| PDF | `application/pdf` | Metadata, download link |
| Google Sheets | `application/vnd.google-apps.spreadsheet` | CSV export, row/column data |
| Excel | `.xlsx` | Spreadsheet parsing |
| Google Docs | `application/vnd.google-apps.document` | Text export |
| Markdown | `text/markdown` | HTML conversion |
| Video | `video/*` | Thumbnail, playback link |

## HTML Card Templates

Generated cards match the existing portal design:

- **Document Card**: PDFs, Word docs
- **Spreadsheet Card**: Excel, Google Sheets
- **Article Card**: Markdown, text files
- **Video Card**: MP4, recordings

All cards include:
- Title with link to Google Drive
- Last modified date
- File size (where applicable)
- Preview/download buttons

## Error Handling

The service includes comprehensive error handling:

1. **API Errors**: Automatic retry with exponential backoff
2. **Parse Errors**: File marked as error, retry on next cycle
3. **Database Errors**: Transaction rollback, logged for review
4. **Network Errors**: Retry after configurable delay

Failed files are automatically retried up to `MAX_RETRIES` times.

## Performance

- **Database Connection Pool**: Reuses connections for efficiency
- **Batch Processing**: Processes files in configurable batches
- **Incremental Updates**: Only syncs changed files
- **Async Operations**: Non-blocking file operations

Typical performance:
- 100 files: ~30 seconds
- 500 files: ~2-3 minutes
- 1000 files: ~5-6 minutes

## Security

- Service account with read-only Drive access
- Database credentials in environment variables
- Secure file permissions (600) on credentials
- SQL injection protection via parameterized queries
- No user input accepted (fully automated)

## Deployment

### As Systemd Service

```bash
sudo systemctl enable gov-portal-sync
sudo systemctl start gov-portal-sync
sudo systemctl status gov-portal-sync
```

### Manual Run

```bash
source venv/bin/activate
python sync_worker.py
```

### Docker (Coming Soon)

Dockerization planned for easier deployment.

## Troubleshooting

### Service won't start
- Check credentials file exists and is readable
- Verify database connection
- Check logs: `tail -f logs/sync.log`

### No files syncing
- Verify folders are shared with service account
- Check folder IDs in database
- Ensure folders have files

### Database errors
- Check PostgreSQL is running
- Verify credentials in `.env`
- Test connection: `psql -U sync_user gov_portal_sync`

See **SETUP_INSTRUCTIONS.md** for detailed troubleshooting.

## Development

### Running Tests

```bash
# Install dev dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/
```

### Adding New File Parsers

1. Create parser class in `parsers/file_parser.py`
2. Inherit from `FileParser` base class
3. Implement `parse()` method
4. Add MIME type mapping in `get_parser()`

### Adding New HTML Templates

1. Create template method in `generators/html_generator.py`
2. Follow existing card structure
3. Update `generate_card()` to use new template

## License

Proprietary - Government Portal Project

## Support

For issues or questions:
- Review logs: `tail -f logs/sync.log`
- Check monitor: `python monitor.py`
- See setup guide: `SETUP_INSTRUCTIONS.md`
