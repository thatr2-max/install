#!/usr/bin/env python3
"""
Generate Configured Site
Creates a complete copy of the government portal with your configuration applied.
This script does NOT modify the original template files.
"""

import os
import sys
import shutil
import json
from datetime import datetime

def print_header():
    print("=" * 70)
    print("  Government Portal Site Generator")
    print("=" * 70)
    print()

def verify_config():
    """Verify user-setup.json exists and is valid"""
    if not os.path.exists('user-setup.json'):
        print("❌ ERROR: user-setup.json not found!")
        print("Please download your configuration from the setup wizard first.")
        sys.exit(1)

    try:
        with open('user-setup.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ Configuration file loaded successfully")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in user-setup.json: {e}")
        sys.exit(1)

def create_output_directory():
    """Create output directory for the configured site"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"configured-site-{timestamp}"

    if os.path.exists(output_dir):
        response = input(f"Directory {output_dir} exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)
    print(f"✓ Created output directory: {output_dir}")
    return output_dir

def copy_site_files(output_dir):
    """Copy all site files to the output directory"""
    print("\nCopying site files...")

    # Files and directories to exclude from copying
    exclude = {
        'configured-site',
        'configured-site-*',
        '.git',
        '.gitignore',
        '__pycache__',
        '*.pyc',
        '.DS_Store',
        'generate-site.py',
        'initialize-site.py'
    }

    files_copied = 0
    for item in os.listdir('.'):
        # Skip excluded items
        if item in exclude or item.startswith('configured-site-'):
            continue

        src = item
        dst = os.path.join(output_dir, item)

        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                files_copied += 1
            else:
                shutil.copy2(src, dst)
                files_copied += 1
        except Exception as e:
            print(f"Warning: Could not copy {item}: {e}")

    print(f"✓ Copied {files_copied} files and directories")

def create_data_loaders(output_dir, config):
    """Create JavaScript data loader files for dynamic content"""

    # Create parks data loader
    parks_loader = """/**
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
    if (!cc.name) return;

    const html = `
      <div class="card">
        <h3>${this.escapeHtml(cc.name)}</h3>
        ${cc.address ? `<p><strong>Address:</strong> ${this.escapeHtml(cc.address)}</p>` : ''}
        ${cc.phone ? `<p><strong>Phone:</strong> <a href="tel:${this.escapeHtml(cc.phone)}">${this.escapeHtml(cc.phone)}</a></p>` : ''}
        ${cc.hours ? `<p><strong>Hours:</strong> ${this.escapeHtml(cc.hours)}</p>` : ''}
        ${cc.amenities && cc.amenities.length > 0 ? `
          <p><strong>Amenities:</strong></p>
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
"""

    # Create staff data loader
    staff_loader = """/**
 * Staff Directory Data Loader
 * Loads staff information from user-setup.json
 */

class StaffDataLoader {
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
      this.loadElectedOfficials();
      this.loadDepartmentHeads();
      this.loadDepartments();
    } catch (error) {
      console.error('Error loading staff data:', error);
    }
  }

  loadElectedOfficials() {
    const container = document.getElementById('elected-officials-list');
    if (!container || !this.config.staff || !this.config.staff.elected_officials) return;

    const officials = this.config.staff.elected_officials;
    if (officials.length === 0) {
      container.innerHTML = '<p><em>No elected officials configured yet.</em></p>';
      return;
    }

    const html = officials.map(official => `
      <div class="card">
        <h3>${this.escapeHtml(official.name)}</h3>
        <p><strong>${this.escapeHtml(official.title)}</strong></p>
        ${official.email ? `<p>Email: <a href="mailto:${this.escapeHtml(official.email)}">${this.escapeHtml(official.email)}</a></p>` : ''}
        ${official.phone ? `<p>Phone: <a href="tel:${this.escapeHtml(official.phone)}">${this.escapeHtml(official.phone)}</a></p>` : ''}
      </div>
    `).join('');

    container.innerHTML = html;
  }

  loadDepartmentHeads() {
    const container = document.getElementById('department-heads-list');
    if (!container || !this.config.staff || !this.config.staff.department_heads) return;

    const heads = this.config.staff.department_heads;
    if (heads.length === 0) {
      container.innerHTML = '<p><em>No department heads configured yet.</em></p>';
      return;
    }

    const html = heads.map(head => `
      <div class="card">
        <h3>${this.escapeHtml(head.name)}</h3>
        <p><strong>${this.escapeHtml(head.title)}</strong></p>
        ${head.department ? `<p><em>${this.escapeHtml(head.department)}</em></p>` : ''}
        ${head.email ? `<p>Email: <a href="mailto:${this.escapeHtml(head.email)}">${this.escapeHtml(head.email)}</a></p>` : ''}
        ${head.phone ? `<p>Phone: <a href="tel:${this.escapeHtml(head.phone)}">${this.escapeHtml(head.phone)}</a></p>` : ''}
      </div>
    `).join('');

    container.innerHTML = html;
  }

  loadDepartments() {
    const container = document.getElementById('departments-list');
    if (!container || !this.config.staff || !this.config.staff.departments) return;

    const departments = this.config.staff.departments;
    if (departments.length === 0) {
      container.innerHTML = '<p><em>No departments configured yet.</em></p>';
      return;
    }

    const html = departments.map(dept => `
      <div class="card">
        <h3>${this.escapeHtml(dept.name)}</h3>
        ${dept.location ? `<p><strong>Location:</strong> ${this.escapeHtml(dept.location)}</p>` : ''}
        ${dept.phone ? `<p><strong>Phone:</strong> <a href="tel:${this.escapeHtml(dept.phone)}">${this.escapeHtml(dept.phone)}</a></p>` : ''}
        ${dept.email ? `<p><strong>Email:</strong> <a href="mailto:${this.escapeHtml(dept.email)}">${this.escapeHtml(dept.email)}</a></p>` : ''}
        ${dept.hours ? `<p><strong>Hours:</strong> ${this.escapeHtml(dept.hours)}</p>` : ''}
        ${dept.services && dept.services.length > 0 ? `
          <p><strong>Services:</strong></p>
          <ul>
            ${dept.services.map(s => `<li>${this.escapeHtml(s)}</li>`).join('')}
          </ul>
        ` : ''}
      </div>
    `).join('');

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
    const loader = new StaffDataLoader();
    loader.init();
  });
} else {
  const loader = new StaffDataLoader();
  loader.init();
}
"""

    # Write the data loaders to the assets/js directory
    js_dir = os.path.join(output_dir, 'assets', 'js')
    os.makedirs(js_dir, exist_ok=True)

    with open(os.path.join(js_dir, 'parks-data-loader.js'), 'w', encoding='utf-8') as f:
        f.write(parks_loader)

    with open(os.path.join(js_dir, 'staff-data-loader.js'), 'w', encoding='utf-8') as f:
        f.write(staff_loader)

    print("✓ Created data loader scripts")

def update_pages_with_containers(output_dir):
    """Update pages to include containers for dynamic content"""

    # Update parks-recreation.html
    parks_page = os.path.join(output_dir, 'pages', 'parks-recreation.html')
    if os.path.exists(parks_page):
        with open(parks_page, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add parks data loader script if not already present
        if 'parks-data-loader.js' not in content:
            content = content.replace(
                '<script src="../assets/js/component-loader.js"></script>',
                '<script src="../assets/js/parks-data-loader.js"></script>\n    <script src="../assets/js/component-loader.js"></script>'
            )

        # Add container divs if they don't exist
        if 'id="parks-list"' not in content:
            # Look for parks section and add container
            # This is a simple approach - in production you'd want more sophisticated HTML parsing
            pass

        with open(parks_page, 'w', encoding='utf-8') as f:
            f.write(content)

    # Update staff-directory.html
    staff_page = os.path.join(output_dir, 'pages', 'staff-directory.html')
    if os.path.exists(staff_page):
        with open(staff_page, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add staff data loader script if not already present
        if 'staff-data-loader.js' not in content:
            content = content.replace(
                '<script src="../assets/js/component-loader.js"></script>',
                '<script src="../assets/js/staff-data-loader.js"></script>\n    <script src="../assets/js/component-loader.js"></script>'
            )

        with open(staff_page, 'w', encoding='utf-8') as f:
            f.write(content)

    print("✓ Updated pages with data loader scripts")

def print_summary(output_dir, config):
    """Print summary of generated site"""
    print("\n" + "=" * 70)
    print("  Site Generation Complete!")
    print("=" * 70)
    print(f"\nYour configured site is ready in: {output_dir}/")
    print("\nConfiguration Summary:")
    print(f"  Municipality: {config.get('municipality', {}).get('name', 'Not set')}")
    print(f"  Council Members: {len(config.get('council_members', []))}")
    print(f"  Form Emails: {len(config.get('form_emails', []))}")
    print(f"  Parks: {len(config.get('parks', []))}")
    print(f"  Trails: {len(config.get('trails', []))}")
    print(f"  Community Center: {'Configured' if config.get('community_center', {}).get('name') else 'Not configured'}")

    staff = config.get('staff', {})
    print(f"  Elected Officials: {len(staff.get('elected_officials', []))}")
    print(f"  Department Heads: {len(staff.get('department_heads', []))}")
    print(f"  Departments: {len(staff.get('departments', []))}")

    print("\nNext Steps:")
    print(f"  1. Navigate to the directory: cd {output_dir}")
    print("  2. Test locally by opening index.html in a browser")
    print("  3. Deploy to your web server or hosting platform")
    print("\nNote: Remember to configure your Google Drive API if you're using")
    print("      Google Drive integration for documents.")
    print()

def main():
    print_header()

    # Step 1: Verify configuration
    print("Step 1: Verifying configuration...")
    config = verify_config()
    print()

    # Step 2: Create output directory
    print("Step 2: Creating output directory...")
    output_dir = create_output_directory()
    print()

    # Step 3: Copy site files
    print("Step 3: Copying site files...")
    copy_site_files(output_dir)
    print()

    # Step 4: Create data loaders
    print("Step 4: Creating data loader scripts...")
    create_data_loaders(output_dir, config)
    print()

    # Step 5: Update pages
    print("Step 5: Updating pages...")
    update_pages_with_containers(output_dir)
    print()

    # Step 6: Print summary
    print_summary(output_dir, config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
