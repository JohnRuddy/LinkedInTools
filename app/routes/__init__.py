from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app, send_file
import requests
import urllib.parse
from app.linkedin_api import LinkedInAPI
from cv_generator import CVGenerator
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Main page - shows login or profile based on authentication status"""
    # Get available CV templates
    cv_generator = CVGenerator()
    available_templates = cv_generator.get_available_templates()
    
    if 'access_token' in session:
        # User is authenticated, get profile data
        linkedin_api = LinkedInAPI(session['access_token'])
        profile = linkedin_api.get_profile()
        
        if profile.get('error'):
            flash(f"Error loading profile: {profile['error']}", 'error')
            return redirect(url_for('main.logout'))
        
        return render_template('index.html', profile=profile, available_templates=available_templates)
    else:
        # User is not authenticated, show login
        return render_template('index.html', available_templates=available_templates)

@main.route('/auth/linkedin')
def linkedin_auth():
    """Initiate LinkedIn OAuth flow"""
    client_id = current_app.config['LINKEDIN_CLIENT_ID']
    redirect_uri = current_app.config['LINKEDIN_REDIRECT_URI']
    
    if not client_id:
        flash('LinkedIn Client ID not configured', 'error')
        return redirect(url_for('main.home'))
    
    # LinkedIn OAuth 2.0 authorization URL
    auth_url = 'https://www.linkedin.com/oauth/v2/authorization'
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': 'profile email openid',
        'state': 'random-state-string'  # In production, use a random state
    }
    
    auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url_with_params)

@main.route('/auth/linkedin/callback')
def linkedin_callback():
    """Handle LinkedIn OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f'LinkedIn authentication failed: {error}', 'error')
        return redirect(url_for('main.home'))
    
    if not code:
        flash('Authorization code not received', 'error')
        return redirect(url_for('main.home'))
    
    # Exchange code for access token
    token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': current_app.config['LINKEDIN_REDIRECT_URI'],
        'client_id': current_app.config['LINKEDIN_CLIENT_ID'],
        'client_secret': current_app.config['LINKEDIN_CLIENT_SECRET']
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()
        
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        if access_token:
            session['access_token'] = access_token
            session['token_type'] = token_data.get('token_type', 'Bearer')
            session['expires_in'] = token_data.get('expires_in')
            
            flash('Successfully authenticated with LinkedIn!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Failed to obtain access token', 'error')
            return redirect(url_for('main.home'))
            
    except requests.RequestException as e:
        flash(f'Error during authentication: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@main.route('/refresh')
def refresh_profile():
    """Refresh profile data"""
    if 'access_token' not in session:
        flash('Please authenticate first', 'error')
        return redirect(url_for('main.home'))
    
    flash('Profile refreshed successfully!', 'success')
    return redirect(url_for('main.home'))

@main.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('main.home'))

@main.route('/generate-cv', methods=['POST'])
def generate_cv():
    """Generate CV based on selected sections using LaTeX templates"""
    if 'access_token' not in session:
        flash('Please authenticate first', 'error')
        return redirect(url_for('main.home'))
    
    selected_sections = request.form.getlist('selected_sections')
    section_order = request.form.get('section_order', '')
    template = request.form.get('template', 'modern')
    format_type = request.form.get('format', 'pdf')
    
    if not selected_sections:
        flash('Please select at least one section to include in your CV', 'error')
        return redirect(url_for('main.home'))
    
    # Get user profile data
    linkedin_api = LinkedInAPI(session['access_token'])
    profile = linkedin_api.get_profile()
    
    if profile.get('error'):
        flash(f"Error loading profile: {profile['error']}", 'error')
        return redirect(url_for('main.home'))
    
    # Parse section order
    ordered_sections = []
    if section_order:
        order_list = section_order.split(',')
        # Reorder selected sections according to user's drag-and-drop order
        for section_id in order_list:
            if section_id in selected_sections:
                ordered_sections.append(section_id)
        # Add any remaining selected sections that weren't in the order
        for section_id in selected_sections:
            if section_id not in ordered_sections:
                ordered_sections.append(section_id)
    else:
        ordered_sections = selected_sections
    
    # Create sample profile data structure for CV generation
    # In a real implementation, you would extract this from LinkedIn API
    cv_profile_data = {
        'name': profile.get('name', 'N/A'),
        'email': profile.get('email', 'N/A'),
        'phone': profile.get('phone', ''),
        'location': profile.get('location', ''),
        'linkedin_url': f"https://linkedin.com/in/{profile.get('vanityName', '')}" if profile.get('vanityName') else '',
        'summary': profile.get('localizedHeadline', ''),
        'experience': [
            {
                'title': 'Software Engineer',
                'company': 'Tech Company',
                'location': 'New York, NY',
                'duration': '2020 - Present',
                'responsibilities': [
                    'Developed web applications using modern technologies',
                    'Collaborated with cross-functional teams',
                    'Participated in code reviews and mentoring'
                ]
            }
        ],
        'education': [
            {
                'degree': 'Bachelor of Science in Computer Science',
                'institution': 'University Name',
                'location': 'City, State',
                'year': '2018',
                'gpa': '3.8'
            }
        ],
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker'],
        'projects': [
            {
                'name': 'LinkedIn CV Generator',
                'duration': '2024',
                'description': 'A web application that generates CVs from LinkedIn profiles',
                'details': [
                    'Built with Flask and LaTeX templates',
                    'Integrated LinkedIn OAuth for authentication',
                    'Supports multiple CV templates and formats'
                ]
            }
        ],
        'certifications': [],
        'languages': [],
        'volunteer': [],
        'honors': []
    }
    
    # Initialize CV generator
    generator = CVGenerator()
    
    # Generate CV
    result = generator.generate_cv(
        profile=cv_profile_data,
        selected_sections=ordered_sections,
        template_name=template,
        output_format=format_type
    )
    
    if result['success']:
        # Store the file info in session for download
        session['cv_file'] = {
            'path': result['file_path'],
            'filename': result['filename'],
            'content_type': result['content_type']
        }
        
        flash(f'CV generated successfully! Template: {template}, Format: {format_type}', 'success')
        return redirect(url_for('main.download_cv'))
    else:
        flash(f'CV generation failed: {result["error"]}', 'error')
        return redirect(url_for('main.home'))

@main.route('/download-cv')
def download_cv():
    """Download the generated CV file"""
    if 'cv_file' not in session:
        flash('No CV file available for download', 'error')
        return redirect(url_for('main.home'))
    
    cv_file = session['cv_file']
    
    if not os.path.exists(cv_file['path']):
        flash('CV file not found', 'error')
        session.pop('cv_file', None)
        return redirect(url_for('main.home'))
    
    try:
        return send_file(
            cv_file['path'],
            as_attachment=True,
            download_name=cv_file['filename'],
            mimetype=cv_file['content_type']
        )
    except Exception as e:
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('main.home'))
