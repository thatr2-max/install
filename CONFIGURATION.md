# Municipality Configuration Guide

This government portal template includes a powerful configuration system that allows you to customize which features are visible without modifying the actual template code.

## Configuration File

All customization is controlled through the `user-setup.json` file in the root directory.

## How to Customize

### 1. Municipality Information

```json
"municipality": {
  "name": "Springfield",
  "banner_image": "assets/images/banner.svg",
  "show_banner": true
}
```

- **name**: Your municipality name (appears in headers and titles)
- **banner_image**: Path to your custom banner image
  - Can be SVG, PNG, JPG, or any web-compatible image format
  - Recommended size: 1200x300px
  - Will automatically resize and crop to fit
- **show_banner**: Set to `false` to hide the banner completely

### 2. Custom Banner Image

To add your own banner:

1. Create your banner image (recommended 1200x300px)
2. Save it to `assets/images/` (e.g., `assets/images/my-city-banner.png`)
3. Update the `banner_image` path in `user-setup.json`:
   ```json
   "banner_image": "assets/images/my-city-banner.png"
   ```

The default banner is an SVG file that you can:
- Replace entirely with your own artwork
- Edit directly (it's an SVG text file)
- Convert to PNG/JPG for your own design

### 3. Quick Actions Bar

Control which quick action buttons appear below the navigation:

```json
"quick_actions": {
  "permits": true,
  "pay_bills": true,
  "report_issue": true,
  "public_records": true
}
```

Set any to `false` to hide that button. If all are `false`, the entire quick actions bar will be hidden.

### 4. Homepage Cards

Control which service cards appear on the homepage:

```json
"homepage_cards": {
  "permits_licenses": true,
  "pay_bills_taxes": true,
  "report_issue": true,
  "public_records": true,
  "community_events": true,
  "staff_directory": true,
  "careers": true,
  "city_council": true,
  "public_services": true,
  "parks_recreation": true,
  "public_safety": true,
  "planning_zoning": true,
  "business_resources": true,
  "resident_services": true,
  "faqs": true,
  "news": true,
  "forms": true,
  "contact": true
}
```

Set any card to `false` to remove it from the homepage.

### 5. Available Pages

Control which pages are available in your portal:

```json
"pages": {
  "accessibility": true,
  "permits": true,
  "pay_bills": true,
  "voting_elections": true,
  "education": true,
  // ... and 60+ more pages
}
```

Pages set to `false` will:
- Not appear in navigation menus
- Not be linked from other pages
- Still be technically accessible if someone has the direct URL

**Note**: The configuration system handles display logic. For complete page removal, you would delete the actual HTML files.

### 6. Footer Links

Control which links appear in the footer:

```json
"footer_links": {
  "accessibility": true,
  "contact": true,
  "faqs": true,
  "careers": true,
  "permits": true,
  "pay_bills": true,
  "report_issue": true,
  "public_records": true,
  "council_meetings": true,
  "staff_directory": true,
  "news": true,
  "forms": true
}
```

## Common Use Cases

### Small Municipality (Limited Services)

```json
{
  "municipality": {
    "name": "Smallville",
    "banner_image": "assets/images/smallville-banner.png",
    "show_banner": true
  },
  "quick_actions": {
    "permits": true,
    "pay_bills": true,
    "report_issue": true,
    "public_records": false
  },
  "homepage_cards": {
    "permits_licenses": true,
    "pay_bills_taxes": true,
    "report_issue": true,
    "public_records": false,
    "community_events": true,
    "staff_directory": true,
    "careers": false,
    "city_council": true,
    // Set others to false as needed
  }
}
```

### Large City (All Services)

Keep all settings at `true` (default configuration).

### Focus on Specific Departments

```json
{
  "homepage_cards": {
    "public_safety": true,
    "emergency_management": true,
    "fire_department": true,
    // Other departments set to false
  }
}
```

## Best Practices

1. **Always validate your JSON**: Use a JSON validator to ensure no syntax errors
2. **Test after changes**: Load the homepage and verify your changes took effect
3. **Keep a backup**: Save a copy of your working configuration
4. **Document your changes**: Add comments in a separate doc file about why certain features are disabled
5. **Update gradually**: Make changes incrementally and test each change

## Troubleshooting

**Changes not appearing?**
- Clear your browser cache (Ctrl+F5 or Cmd+Shift+R)
- Check browser console for errors (F12)
- Validate your JSON syntax

**Banner not loading?**
- Verify the image file exists at the specified path
- Check file permissions
- Try using an absolute URL for testing

**Some elements still visible when set to false?**
- The configuration affects homepage and navigation
- Direct page access via URL may still work
- Some cached content may persist until browser refresh

## Advanced Customization

For deeper customization beyond the configuration file:
- Edit `assets/css/styles.css` for visual styling
- Modify individual page HTML files for content
- Update `assets/js/config-loader.js` for configuration logic

## Support

For technical issues or questions about configuration:
1. Check browser console for errors
2. Validate your JSON at jsonlint.com
3. Refer to this guide for proper syntax
