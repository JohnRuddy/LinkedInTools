import os
import tempfile
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright
import asyncio
import subprocess
import re


class HTMLCVGenerator:
    def __init__(self, templates_dir='cv_templates_html'):
        self.templates_dir = templates_dir
        self.output_dir = 'generated_cvs'
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def get_available_templates(self):
        """Get list of available HTML template files"""
        if not os.path.exists(self.templates_dir):
            return []
        
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.html'):
                template_name = filename[:-5]  # Remove .html extension
                template_title = template_name.replace('_', ' ').title()
                templates.append({
                    'name': template_name,
                    'title': template_title,
                    'filename': filename
                })
        
        return sorted(templates, key=lambda x: x['name'])
    
    def escape_html(self, text):
        """Escape HTML special characters"""
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # HTML special characters that need escaping
        html_escape_chars = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#x27;',
        }
        
        for char, replacement in html_escape_chars.items():
            text = text.replace(char, replacement)
        
        return text
    
    def prepare_profile_data(self, profile, selected_sections):
        """Prepare and sanitize profile data for HTML"""
        if not profile:
            return {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '+1 (555) 123-4567',
                'location': 'City, State',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
                'summary': 'Professional summary not available.',
                'experience': [],
                'education': [],
                'skills': [],
                'projects': [],
                'certifications': [],
                'languages': [],
                'volunteer': [],
                'honors': []
            }
        
        # Sanitize all text fields
        sanitized_profile = {}
        
        # Basic information (escape HTML)
        sanitized_profile['name'] = self.escape_html(
            f"{profile.get('localizedFirstName', 'John')} {profile.get('localizedLastName', 'Doe')}"
        )
        sanitized_profile['email'] = self.escape_html(profile.get('email', 'john.doe@example.com'))
        sanitized_profile['phone'] = self.escape_html(profile.get('phone', '+1 (555) 123-4567'))
        sanitized_profile['location'] = self.escape_html(profile.get('location', 'City, State'))
        sanitized_profile['linkedin_url'] = profile.get('linkedin_url', 'https://linkedin.com/in/johndoe')
        sanitized_profile['summary'] = self.escape_html(
            profile.get('localizedHeadline', 'Professional summary not available.')
        )
        
        # Initialize empty lists for all sections
        for section in ['experience', 'education', 'skills', 'projects', 'certifications', 
                       'languages', 'volunteer', 'honors']:
            sanitized_profile[section] = []
        
        # Add sample data for demonstration (escape all text)
        if 'experience' in selected_sections:
            sanitized_profile['experience'] = [
                {
                    'title': self.escape_html('Software Developer'),
                    'company': self.escape_html('Tech Company Inc.'),
                    'duration': self.escape_html('Jan 2020 - Present'),
                    'location': self.escape_html('Remote'),
                    'responsibilities': [
                        self.escape_html('Developed and maintained web applications using Python and JavaScript.'),
                        self.escape_html('Collaborated with cross-functional teams to deliver high-quality products.'),
                        self.escape_html('Implemented responsive designs and optimized application performance.')
                    ]
                }
            ]
        
        if 'education' in selected_sections:
            sanitized_profile['education'] = [
                {
                    'degree': self.escape_html('Bachelor of Science in Computer Science'),
                    'institution': self.escape_html('University of Technology'),
                    'duration': self.escape_html('Aug. 2018 - May 2021'),
                    'location': self.escape_html('City, State'),
                    'year': self.escape_html('2021'),
                    'gpa': self.escape_html('3.8/4.0')
                }
            ]
        
        if 'skills' in selected_sections:
            sanitized_profile['skills'] = [
                'Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Docker', 'AWS',
                'HTML/CSS', 'TypeScript', 'Flask', 'Django', 'PostgreSQL', 'MongoDB'
            ]
        
        if 'projects' in selected_sections:
            sanitized_profile['projects'] = [
                {
                    'name': self.escape_html('LinkedIn CV Generator'),
                    'duration': self.escape_html('2023'),
                    'description': self.escape_html('A web application that integrates with LinkedIn API to generate professional CVs.'),
                    'details': [
                        self.escape_html('Built with Flask and integrated LinkedIn OAuth for profile data'),
                        self.escape_html('Implemented HTML/CSS templates for professional CV generation'),
                        self.escape_html('Added drag-and-drop section reordering with responsive design')
                    ]
                }
            ]
        
        if 'certifications' in selected_sections:
            sanitized_profile['certifications'] = [
                {
                    'name': self.escape_html('AWS Certified Solutions Architect'),
                    'issuer': self.escape_html('Amazon Web Services'),
                    'date': self.escape_html('2023'),
                    'credential_id': self.escape_html('AWS-ASA-123456')
                }
            ]
        
        return sanitized_profile
    
    def generate_cv(self, profile, selected_sections, template_name='modern', output_format='pdf'):
        """Generate CV using HTML template and Playwright"""
        
        try:
            # Get template
            template_filename = f"{template_name}.html"
            if not os.path.exists(os.path.join(self.templates_dir, template_filename)):
                return {'success': False, 'error': f'Template {template_name} not found'}
            
            template = self.env.get_template(template_filename)
            
            # Prepare data
            prepared_data = self.prepare_profile_data(profile, selected_sections)
            
            # Render template
            html_content = template.render(
                profile=prepared_data,
                selected_sections=selected_sections
            )
            
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if output_format == 'html':
                # Save as HTML file
                html_filename = f'cv_{template_name}_{timestamp}.html'
                html_path = os.path.join(self.output_dir, html_filename)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return {
                    'success': True,
                    'filename': html_filename,
                    'path': html_path,
                    'content_type': 'text/html'
                }
            
            elif output_format == 'pdf':
                # Convert to PDF using Playwright
                return self._generate_pdf(html_content, template_name, timestamp)
            
            elif output_format == 'docx':
                # For now, return HTML - DOCX conversion can be added later
                return {'success': False, 'error': 'DOCX format not yet supported. Please use PDF or HTML.'}
            
            else:
                return {'success': False, 'error': f'Unsupported output format: {output_format}'}
        
        except Exception as e:
            return {'success': False, 'error': f'CV generation failed: {str(e)}'}
    
    def _generate_pdf(self, html_content, template_name, timestamp):
        """Generate PDF from HTML using Playwright"""
        try:
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set content
                page.set_content(html_content, wait_until='networkidle')
                
                # Generate PDF
                pdf_filename = f'cv_{template_name}_{timestamp}.pdf'
                pdf_path = os.path.join(self.output_dir, pdf_filename)
                
                # PDF options optimized for CV
                page.pdf(
                    path=pdf_path,
                    format='A4',
                    margin={
                        'top': '10mm',
                        'bottom': '10mm',
                        'left': '10mm',
                        'right': '10mm'
                    },
                    print_background=True,
                    prefer_css_page_size=True
                )
                
                browser.close()
                
                return {
                    'success': True,
                    'filename': pdf_filename,
                    'path': pdf_path,
                    'content_type': 'application/pdf'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'PDF generation failed: {str(e)}'
            }
    
    def preview_cv(self, profile, selected_sections, template_name='modern'):
        """Generate HTML preview of CV"""
        try:
            template_filename = f"{template_name}.html"
            if not os.path.exists(os.path.join(self.templates_dir, template_filename)):
                return {'success': False, 'error': f'Template {template_name} not found'}
            
            template = self.env.get_template(template_filename)
            prepared_data = self.prepare_profile_data(profile, selected_sections)
            
            html_content = template.render(
                profile=prepared_data,
                selected_sections=selected_sections
            )
            
            return {
                'success': True,
                'html_content': html_content
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Preview generation failed: {str(e)}'}


# Legacy wrapper for backward compatibility
class CVGenerator(HTMLCVGenerator):
    """Backward compatibility wrapper"""
    
    def __init__(self, templates_dir='cv_templates_html'):
        super().__init__(templates_dir)
        # Also check for LaTeX templates for backward compatibility
        self.latex_templates_dir = 'cv_templates'
    
    def get_available_templates(self):
        """Get both HTML and LaTeX templates"""
        html_templates = super().get_available_templates()
        
        # Also check for LaTeX templates
        latex_templates = []
        if os.path.exists(self.latex_templates_dir):
            for filename in os.listdir(self.latex_templates_dir):
                if filename.endswith('.tex'):
                    template_name = filename[:-4]  # Remove .tex extension
                    template_title = f"{template_name.replace('_', ' ').title()} (LaTeX)"
                    latex_templates.append({
                        'name': f"{template_name}_latex",
                        'title': template_title,
                        'filename': filename,
                        'type': 'latex'
                    })
        
        # Mark HTML templates
        for template in html_templates:
            template['type'] = 'html'
        
        return sorted(html_templates + latex_templates, key=lambda x: x['name'])
    
    def generate_cv(self, profile, selected_sections, template_name='modern', output_format='pdf'):
        """Generate CV with support for both HTML and LaTeX templates"""
        
        # Check if it's a LaTeX template
        if template_name.endswith('_latex'):
            actual_template_name = template_name.replace('_latex', '')
            # Import and use the original LaTeX generator
            from cv_generator_latex import LaTeXCVGenerator
            latex_generator = LaTeXCVGenerator()
            return latex_generator.generate_cv(profile, selected_sections, actual_template_name, output_format)
        
        # Use HTML generator
        return super().generate_cv(profile, selected_sections, template_name, output_format)
