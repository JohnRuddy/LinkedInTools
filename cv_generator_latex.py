import os
import subprocess
import tempfile
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import re

class CVGenerator:
    def __init__(self, templates_dir='cv_templates'):
        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    def check_latex_installation(self):
        """Check if LaTeX is installed and available"""
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                   capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False
    
    def get_available_templates(self):
        """Get list of available template files"""
        if not os.path.exists(self.templates_dir):
            return []
        
        templates = []
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.tex'):
                template_name = filename[:-4]  # Remove .tex extension
                template_title = template_name.replace('_', ' ').title()
                templates.append({
                    'name': template_name,
                    'title': template_title,
                    'filename': filename
                })
        
        return sorted(templates, key=lambda x: x['name'])
    
    def escape_latex(self, text):
        """Escape special LaTeX characters"""
        if not text:
            return ""
        
        # Convert to string if not already
        text = str(text)
        
        # LaTeX special characters that need escaping
        latex_special_chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '^': r'\textasciicircum{}',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '\\': r'\textbackslash{}',
        }
        
        for char, replacement in latex_special_chars.items():
            text = text.replace(char, replacement)
        
        return text
    
    def prepare_profile_data(self, profile, selected_sections):
        """Prepare and sanitize profile data for LaTeX"""
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
        
        # Basic information
        sanitized_profile['name'] = self.escape_latex(
            f"{profile.get('localizedFirstName', 'John')} {profile.get('localizedLastName', 'Doe')}"
        )
        sanitized_profile['email'] = self.escape_latex(profile.get('email', 'john.doe@example.com'))
        sanitized_profile['phone'] = self.escape_latex(profile.get('phone', '+1 (555) 123-4567'))
        sanitized_profile['location'] = self.escape_latex(profile.get('location', 'City, State'))
        sanitized_profile['linkedin_url'] = profile.get('linkedin_url', 'https://linkedin.com/in/johndoe')
        sanitized_profile['summary'] = self.escape_latex(
            profile.get('localizedHeadline', 'Professional summary not available.')
        )
        
        # Initialize empty lists for all sections
        for section in ['experience', 'education', 'skills', 'projects', 'certifications', 
                       'languages', 'volunteer', 'honors']:
            sanitized_profile[section] = []
        
        # Add sample data for demonstration
        if 'experience' in selected_sections:
            sanitized_profile['experience'] = [
                {
                    'title': 'Software Developer',
                    'company': 'Tech Company Inc.',
                    'duration': 'Jan 2020 - Present',
                    'description': 'Developed and maintained web applications using Python and JavaScript.'
                }
            ]
        
        if 'education' in selected_sections:
            sanitized_profile['education'] = [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'school': 'University of Technology',
                    'duration': '2016 - 2020',
                    'description': 'Graduated with honors, GPA: 3.8/4.0'
                }
            ]
        
        if 'skills' in selected_sections:
            sanitized_profile['skills'] = [
                'Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Git', 'Docker', 'AWS'
            ]
        
        return sanitized_profile
    
    def generate_cv(self, profile, selected_sections, template_name='modern', output_format='pdf'):
        """Generate CV using LaTeX template"""
        
        # Check if LaTeX is installed
        if not self.check_latex_installation():
            return {
                'success': False,
                'error': 'LaTeX (pdflatex) is not installed. Please install texlive-latex-base or texlive-full.',
                'installation_help': {
                    'ubuntu': 'sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra',
                    'macos': 'brew install --cask mactex',
                    'general': 'Please install LaTeX distribution for your operating system'
                }
            }
        
        try:
            # Get template
            template_filename = f"{template_name}.tex"
            if not os.path.exists(os.path.join(self.templates_dir, template_filename)):
                return {'success': False, 'error': f'Template {template_name} not found'}
            
            template = self.env.get_template(template_filename)
            
            # Prepare data
            prepared_data = self.prepare_profile_data(profile, selected_sections)
            
            # Render template
            rendered_latex = template.render(
                profile=prepared_data,
                selected_sections=selected_sections
            )
            
            # Create temporary directory for compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write LaTeX file
                tex_file = os.path.join(temp_dir, 'cv.tex')
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(rendered_latex)
                
                if output_format == 'latex':
                    # Return LaTeX source
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"cv_{timestamp}.tex"
                    output_path = os.path.join('downloads', output_filename)
                    
                    os.makedirs('downloads', exist_ok=True)
                    shutil.copy2(tex_file, output_path)
                    
                    return {
                        'success': True,
                        'filename': output_filename,
                        'path': output_path,
                        'content_type': 'application/x-tex'
                    }
                
                # Compile to PDF
                try:
                    result = subprocess.run(
                        ['pdflatex', '-interaction=nonstopmode', 'cv.tex'],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode != 0:
                        return {
                            'success': False,
                            'error': f'LaTeX compilation failed: {result.stderr}',
                            'latex_output': result.stdout
                        }
                    
                    # Check if PDF was created
                    pdf_file = os.path.join(temp_dir, 'cv.pdf')
                    if not os.path.exists(pdf_file):
                        return {
                            'success': False,
                            'error': 'PDF file was not created',
                            'latex_output': result.stdout
                        }
                    
                    # Copy PDF to downloads directory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_filename = f"cv_{timestamp}.pdf"
                    output_path = os.path.join('downloads', output_filename)
                    
                    os.makedirs('downloads', exist_ok=True)
                    shutil.copy2(pdf_file, output_path)
                    
                    return {
                        'success': True,
                        'filename': output_filename,
                        'path': output_path,
                        'content_type': 'application/pdf'
                    }
                    
                except subprocess.TimeoutExpired:
                    return {
                        'success': False,
                        'error': 'LaTeX compilation timed out (30 seconds)'
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Compilation error: {str(e)}'
                    }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error during CV generation: {str(e)}'
            }
