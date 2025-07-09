from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
import requests
import urllib.parse
from app.linkedin_api import LinkedInAPI

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Main page - shows login or profile based on authentication status"""
    if 'access_token' in session:
        # User is authenticated, get profile data
        linkedin_api = LinkedInAPI(session['access_token'])
        profile = linkedin_api.get_profile()
        
        if profile.get('error'):
            flash(f"Error loading profile: {profile['error']}", 'error')
            return redirect(url_for('main.logout'))
        
        return render_template('index.html', profile=profile)
    else:
        # User is not authenticated, show login
        return render_template('index.html')

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
        'scope': 'r_liteprofile r_emailaddress w_member_social',
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