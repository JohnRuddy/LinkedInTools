# CV Templates

This directory contains LaTeX templates for generating professional CVs from LinkedIn profile data.

## Available Templates

### 1. Modern (`modern.tex`)
- Clean, professional design with colors and icons
- Uses FontAwesome icons
- Suitable for tech and creative industries
- Features: colored headers, skill boxes, contact icons

### 2. Classic (`classic.tex`)
- Traditional, conservative design
- Black and white styling
- Suitable for formal industries (finance, law, academia)
- Features: clean typography, minimal formatting

### 3. Minimalist (`minimalist.tex`)
- Simple, clean design with subtle accents
- Focus on content over decoration
- Suitable for most industries
- Features: simple color scheme, clean lines

### 4. Creative (`creative.tex`)
- Colorful, modern design with boxes and highlights
- Eye-catching layout
- Suitable for creative industries (design, marketing)
- Features: colored boxes, creative layouts, multiple colors

## Template Structure

Each template uses Jinja2 templating syntax to dynamically insert profile data:

```latex
{{ profile.name }}           # User's full name
{{ profile.email }}          # Email address
{{ profile.phone }}          # Phone number (optional)
{{ profile.location }}       # Location
{{ profile.linkedin_url }}   # LinkedIn profile URL
{{ profile.summary }}        # Professional summary
```

### Conditional Sections

Sections are included based on the `selected_sections` list:

```latex
{% if 'experience' in selected_sections %}
\section{EXPERIENCE}
{% for experience in profile.experience %}
...
{% endfor %}
{% endif %}
```

### Data Structure

The templates expect the following data structure:

```python
profile = {
    'name': str,
    'email': str,
    'phone': str (optional),
    'location': str (optional),
    'linkedin_url': str (optional),
    'summary': str,
    'experience': [
        {
            'title': str,
            'company': str,
            'location': str,
            'duration': str,
            'responsibilities': [str, ...]
        }
    ],
    'education': [
        {
            'degree': str,
            'institution': str,
            'location': str,
            'year': str,
            'gpa': str (optional)
        }
    ],
    'skills': [str, ...],
    'projects': [
        {
            'name': str,
            'duration': str,
            'description': str,
            'details': [str, ...]
        }
    ],
    'certifications': [
        {
            'name': str,
            'issuer': str,
            'date': str,
            'credential_id': str (optional)
        }
    ],
    'languages': [
        {
            'name': str,
            'level': str
        }
    ],
    'volunteer': [
        {
            'role': str,
            'organization': str,
            'location': str,
            'duration': str,
            'description': str
        }
    ],
    'honors': [
        {
            'name': str,
            'issuer': str,
            'date': str,
            'description': str
        }
    ]
}
```

## LaTeX Requirements

To compile these templates, you need:

### Required Packages
- `inputenc` - UTF-8 encoding
- `fontenc` - Font encoding
- `geometry` - Page margins
- `hyperref` - Hyperlinks
- `enumitem` - List formatting
- `titlesec` - Section formatting
- `xcolor` - Colors
- `fontawesome5` - Icons (for modern and creative templates)
- `tikz` - Graphics (for creative template)
- `tcolorbox` - Colored boxes (for creative template)
- `multicol` - Multiple columns
- `graphicx` - Graphics support
- `tabularx` - Advanced tables

### Installation Commands

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

#### macOS (with Homebrew):
```bash
brew install --cask mactex
```

#### Windows:
Download and install MiKTeX or TeX Live from their official websites.

### FontAwesome Setup

For templates using FontAwesome icons, ensure you have the `fontawesome5` package:

```bash
# Usually included in texlive-full, but if needed:
tlmgr install fontawesome5
```

## Customizing Templates

### Adding New Sections

1. Add the section check:
```latex
{% if 'new_section' in selected_sections %}
\section{NEW SECTION}
<!-- Your content here -->
{% endif %}
```

2. Update the `CVGenerator` class to handle the new data structure.

### Modifying Styling

Each template has its own styling defined at the top:

- **Colors**: Modify `\definecolor` commands
- **Fonts**: Change font packages and commands
- **Layout**: Adjust `geometry` settings
- **Spacing**: Modify `\titlespacing` and `\setlength` commands

### Creating New Templates

1. Create a new `.tex` file in this directory
2. Follow the existing template structure
3. Use Jinja2 syntax for dynamic content
4. Test with sample data
5. Update the template dropdown in the web interface

## Troubleshooting

### Common Issues

1. **Missing packages**: Install the full LaTeX distribution
2. **Font issues**: Ensure FontAwesome is properly installed
3. **Compilation errors**: Check LaTeX syntax and special character escaping
4. **Encoding issues**: Ensure UTF-8 encoding is properly set

### Error Messages

- `! LaTeX Error: File 'fontawesome5.sty' not found`: Install FontAwesome package
- `! Package inputenc Error`: Check UTF-8 encoding
- `! Undefined control sequence`: Check for typos in LaTeX commands

## Contributing

When adding new templates:

1. Follow the existing naming convention
2. Include proper documentation
3. Test with various data combinations
4. Ensure cross-platform compatibility
5. Add fallback content for missing data
