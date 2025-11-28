/**
 * Google Drive File Loader
 * Automatically loads and displays files from Google Drive folders
 * Configure folders in user-setup.json
 */

class GoogleDriveLoader {
  constructor() {
    this.config = null;
    this.apiKey = null;
    this.basePath = window.location.pathname.includes('/pages/') ? '../' : '';
  }

  async init() {
    try {
      // Load configuration
      const response = await fetch(`${this.basePath}user-setup.json`);
      if (!response.ok) {
        console.warn('Could not load user-setup.json');
        return;
      }

      const config = await response.json();
      this.config = config.google_drive;

      // Check if enabled and configured
      if (!this.config || !this.config.enabled) {
        console.log('Google Drive integration is disabled');
        return;
      }

      if (!this.config.api_key || this.config.api_key === 'YOUR_GOOGLE_API_KEY_HERE') {
        console.warn('Google Drive API key not configured. See GOOGLE_DRIVE_SETUP.md');
        this.showSetupMessage();
        return;
      }

      this.apiKey = this.config.api_key;

      // Load files for any drive-file-list elements on the page
      const fileListElements = document.querySelectorAll('[data-drive-folder]');
      fileListElements.forEach(element => {
        const folderKey = element.getAttribute('data-drive-folder');
        this.loadFolderFiles(folderKey, element);
      });

    } catch (error) {
      console.error('Error initializing Google Drive loader:', error);
    }
  }

  async loadFolderFiles(folderKey, containerElement) {
    const folderId = this.config.folders[folderKey];

    if (!folderId) {
      containerElement.innerHTML = `
        <div class="drive-setup-notice">
          <p><strong>Google Drive folder not configured</strong></p>
          <p>To display files here, add the folder ID for "${folderKey}" in user-setup.json</p>
        </div>
      `;
      return;
    }

    // Show loading state
    containerElement.innerHTML = '<p class="drive-loading">Loading files from Google Drive...</p>';

    try {
      const files = await this.fetchFilesFromFolder(folderId);

      if (files.length === 0) {
        containerElement.innerHTML = '<p class="drive-no-files">No files found in this folder.</p>';
        return;
      }

      // Sort files by modified date (newest first)
      files.sort((a, b) => new Date(b.modifiedTime) - new Date(a.modifiedTime));

      // Display files
      this.renderFileList(files, containerElement);

    } catch (error) {
      console.error(`Error loading files from folder ${folderKey}:`, error);
      containerElement.innerHTML = `
        <div class="drive-error">
          <p><strong>Error loading files</strong></p>
          <p>Could not load files from Google Drive. Check console for details.</p>
        </div>
      `;
    }
  }

  async fetchFilesFromFolder(folderId) {
    const baseUrl = 'https://www.googleapis.com/drive/v3/files';
    const params = new URLSearchParams({
      q: `'${folderId}' in parents and trashed=false`,
      key: this.apiKey,
      fields: 'files(id,name,mimeType,size,modifiedTime,webViewLink,webContentLink,iconLink)',
      orderBy: 'modifiedTime desc',
      pageSize: '100'
    });

    const response = await fetch(`${baseUrl}?${params}`);

    if (!response.ok) {
      throw new Error(`Google Drive API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.files || [];
  }

  renderFileList(files, container) {
    const html = `
      <div class="drive-file-list">
        ${files.map(file => this.renderFileItem(file)).join('')}
      </div>
    `;
    container.innerHTML = html;
  }

  renderFileItem(file) {
    const date = new Date(file.modifiedTime);
    const formattedDate = date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });

    const size = file.size ? this.formatFileSize(file.size) : '';
    const fileType = this.getFileType(file.mimeType, file.name);
    const downloadLink = file.webContentLink || file.webViewLink;

    return `
      <div class="drive-file-item">
        <div class="drive-file-icon">
          ${this.getFileIcon(fileType)}
        </div>
        <div class="drive-file-info">
          <div class="drive-file-name">
            <a href="${downloadLink}" target="_blank" rel="noopener">${this.escapeHtml(file.name)}</a>
          </div>
          <div class="drive-file-meta">
            <span class="drive-file-date">${formattedDate}</span>
            ${size ? `<span class="drive-file-size">${size}</span>` : ''}
            <span class="drive-file-type">${fileType}</span>
          </div>
        </div>
      </div>
    `;
  }

  getFileType(mimeType, filename) {
    if (mimeType.includes('pdf')) return 'PDF';
    if (mimeType.includes('word') || filename.endsWith('.docx') || filename.endsWith('.doc')) return 'Word';
    if (mimeType.includes('excel') || filename.endsWith('.xlsx') || filename.endsWith('.xls')) return 'Excel';
    if (mimeType.includes('powerpoint') || filename.endsWith('.pptx') || filename.endsWith('.ppt')) return 'PowerPoint';
    if (mimeType.includes('video')) return 'Video';
    if (mimeType.includes('audio')) return 'Audio';
    if (mimeType.includes('image')) return 'Image';
    if (mimeType.includes('text')) return 'Text';
    return 'File';
  }

  getFileIcon(fileType) {
    const icons = {
      'PDF': '📄',
      'Word': '📝',
      'Excel': '📊',
      'PowerPoint': '📊',
      'Video': '🎥',
      'Audio': '🎵',
      'Image': '🖼️',
      'Text': '📃',
      'File': '📁'
    };
    return icons[fileType] || icons['File'];
  }

  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  showSetupMessage() {
    const elements = document.querySelectorAll('[data-drive-folder]');
    elements.forEach(element => {
      element.innerHTML = `
        <div class="drive-setup-notice">
          <h3>📁 Google Drive Setup Required</h3>
          <p>To display files from Google Drive:</p>
          <ol>
            <li>Get a Google API key (see GOOGLE_DRIVE_SETUP.md)</li>
            <li>Add it to user-setup.json → google_drive.api_key</li>
            <li>Add folder IDs to user-setup.json → google_drive.folders</li>
          </ol>
        </div>
      `;
    });
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const loader = new GoogleDriveLoader();
    loader.init();
  });
} else {
  const loader = new GoogleDriveLoader();
  loader.init();
}
