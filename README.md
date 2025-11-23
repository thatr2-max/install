# Accessible Government Website Templates

A comprehensive collection of 20 accessible, WCAG 2.1 AA compliant website templates designed specifically for government services.

## Overview

This project provides a complete set of HTML templates for a city government website with a strong focus on accessibility, usability, and inclusive design. Every page is designed to be accessible to all users, including those using assistive technologies.

## Features

### Accessibility-First Design

- **WCAG 2.1 Level AA Compliant**: Meets Web Content Accessibility Guidelines standards
- **Screen Reader Optimized**: Semantic HTML, ARIA labels, and proper heading hierarchy
- **Keyboard Navigation**: Full keyboard accessibility with visible focus indicators
- **Skip Navigation Links**: Quick access to main content
- **High Contrast**: Text meets minimum 4.5:1 contrast ratios
- **Responsive Design**: Works on all devices and screen sizes
- **Alternative Text**: All images include descriptive alt text
- **Form Accessibility**: Clear labels, error messages, and required field indicators

### Included Pages (20 Templates)

1. **index.html** - Main portal with navigation to all services
2. **permits.html** - Apply for permits and licenses
3. **staff-directory.html** - Contact city officials and staff
4. **pay-bills.html** - Pay taxes, utilities, and citations
5. **report-issue.html** - Report municipal issues
6. **public-records.html** - Request public documents
7. **events.html** - Community events and calendar
8. **contact.html** - Contact information and forms
9. **careers.html** - Employment opportunities
10. **council-meetings.html** - City council information
11. **public-services.html** - Water, trash, utilities
12. **parks-recreation.html** - Parks and recreation programs
13. **public-safety.html** - Police and fire services
14. **planning-zoning.html** - Zoning and development
15. **business-resources.html** - Business support services
16. **resident-services.html** - Voter registration, licenses
17. **accessibility.html** - Accessibility statement
18. **faqs.html** - Frequently asked questions
19. **news.html** - News and press releases
20. **forms.html** - Downloadable forms and documents

## Technical Specifications

### HTML
- Semantic HTML5 markup
- ARIA landmarks and roles
- Proper heading hierarchy (H1-H6)
- Descriptive link text
- Form labels and fieldsets
- Table headers and captions

### CSS
- Mobile-first responsive design
- High contrast color scheme
- Flexible layouts with CSS Grid and Flexbox
- Print-friendly styles
- Support for user preferences:
  - Prefers reduced motion
  - Prefers high contrast
- Clear focus indicators

### Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Internet Explorer 11 (graceful degradation)
- Mobile browsers (iOS Safari, Chrome Android)

### Assistive Technology Compatibility
- JAWS
- NVDA
- VoiceOver
- TalkBack
- Dragon NaturallySpeaking
- Screen magnification software

## File Structure

```
/
├── index.html                 # Main homepage
├── assets/
│   ├── css/
│   │   └── styles.css        # Shared stylesheet
│   └── js/                   # (Optional JavaScript)
├── pages/
│   ├── accessibility.html
│   ├── business-resources.html
│   ├── careers.html
│   ├── contact.html
│   ├── council-meetings.html
│   ├── events.html
│   ├── faqs.html
│   ├── forms.html
│   ├── news.html
│   ├── parks-recreation.html
│   ├── pay-bills.html
│   ├── permits.html
│   ├── planning-zoning.html
│   ├── public-records.html
│   ├── public-safety.html
│   ├── public-services.html
│   ├── report-issue.html
│   ├── resident-services.html
│   └── staff-directory.html
└── README.md
```

## Getting Started

### Local Development

1. Clone the repository
2. Open `index.html` in a web browser
3. No build process required - pure HTML/CSS

### Deployment

Upload all files to your web server maintaining the directory structure. Ensure:
- All links use relative paths
- CSS file is accessible from all pages
- Server supports UTF-8 encoding

### Customization

#### Colors
Edit CSS custom properties in `assets/css/styles.css`:
```css
:root {
  --primary-color: #0066cc;
  --text-color: #1a202c;
  /* etc. */
}
```

#### Content
- Replace placeholder text with your city's information
- Update contact information throughout
- Add real links to forms and documents
- Replace example staff names and departments

#### Branding
- Add your city logo to the header
- Update the site title and tagline
- Customize footer content

## Accessibility Testing

This project has been designed with accessibility in mind. Recommended testing:

- **Automated Testing**: Use tools like axe DevTools, WAVE, or Lighthouse
- **Screen Reader Testing**: Test with JAWS, NVDA, or VoiceOver
- **Keyboard Navigation**: Ensure all functionality works without a mouse
- **Color Contrast**: Verify all text meets WCAG AA standards
- **Zoom Testing**: Test at 200% zoom level
- **Mobile Testing**: Test on various mobile devices

## Compliance

These templates are designed to meet:
- WCAG 2.1 Level AA
- Section 508 (U.S. Federal)
- ADA Title II (Americans with Disabilities Act)

## Best Practices

### Maintaining Accessibility
- Test with real users who use assistive technology
- Provide alternative formats for documents (large print, braille)
- Offer multiple ways to contact (phone, email, in-person)
- Train staff on accessibility requirements
- Regularly audit for accessibility issues

### Content Guidelines
- Use clear, plain language
- Break up long paragraphs
- Use bullet points and lists
- Provide context for links
- Include descriptive headings

## Support

For questions about these templates:
- Review the [Accessibility Statement](pages/accessibility.html)
- Check the [FAQs](pages/faqs.html)
- Contact: accessibility@citygovernment.gov

## License

This project is released for public use by government entities.

## Contributing

Improvements and suggestions are welcome! Please ensure any contributions maintain or enhance accessibility standards.

## Credits

Designed and developed with a focus on universal accessibility and inclusive design.

---

**Remember**: Accessibility is not a feature—it's a requirement. These templates provide a foundation, but ongoing testing and user feedback are essential for true accessibility.
