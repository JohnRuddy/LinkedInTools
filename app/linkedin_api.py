import requests
import json

class LinkedInAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://api.linkedin.com/v2'
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    def get_profile(self):
        """Get user's basic profile information"""
        try:
            # Get basic profile info using current LinkedIn API v2
            profile_url = f'{self.base_url}/userinfo'
            
            response = requests.get(profile_url, headers=self.headers)
            response.raise_for_status()
            
            profile_data = response.json()
            
            # Transform the response to match our template expectations
            transformed_data = {
                'id': profile_data.get('sub'),
                'localizedFirstName': profile_data.get('given_name'),
                'localizedLastName': profile_data.get('family_name'),
                'localizedHeadline': profile_data.get('locale', {}).get('country') if isinstance(profile_data.get('locale'), dict) else None,
                'email': profile_data.get('email'),
                'name': profile_data.get('name'),
                'picture': profile_data.get('picture')
            }
            
            # Get profile sections for CV generation
            sections = self._get_profile_sections()
            transformed_data['sections'] = sections
            
            return transformed_data
            
        except requests.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'JSON decode error: {str(e)}'}
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}
    
    def _get_profile_sections(self):
        """Get available profile sections for CV generation"""
        # Since LinkedIn API v2 has limited public access, we'll simulate the sections
        # that would typically be available from a LinkedIn profile
        sections = []
        
        # Basic profile sections that are commonly available
        available_sections = [
            {'id': 'personal_info', 'name': 'Personal Information', 'description': 'Name, contact details, location'},
            {'id': 'summary', 'name': 'Professional Summary', 'description': 'About section and professional headline'},
            {'id': 'experience', 'name': 'Work Experience', 'description': 'Employment history and job roles'},
            {'id': 'education', 'name': 'Education', 'description': 'Educational background and qualifications'},
            {'id': 'skills', 'name': 'Skills & Endorsements', 'description': 'Professional skills and competencies'},
            {'id': 'certifications', 'name': 'Certifications', 'description': 'Professional certifications and licenses'},
            {'id': 'projects', 'name': 'Projects', 'description': 'Notable projects and achievements'},
            {'id': 'languages', 'name': 'Languages', 'description': 'Language proficiencies'},
            {'id': 'publications', 'name': 'Publications', 'description': 'Articles, papers, and publications'},
            {'id': 'honors', 'name': 'Honors & Awards', 'description': 'Recognition and achievements'},
            {'id': 'volunteer', 'name': 'Volunteer Experience', 'description': 'Volunteer work and community involvement'},
            {'id': 'recommendations', 'name': 'Recommendations', 'description': 'Professional recommendations'}
        ]
        
        # In a real implementation, you would check if each section has data
        # For now, we'll mark all sections as available
        for section in available_sections:
            sections.append({
                'id': section['id'],
                'name': section['name'],
                'description': section['description'],
                'has_data': True,  # In real implementation, check if section has data
                'selected': False  # Default selection state
            })
        
        return sections
    
    def get_profile_picture(self):
        """Get user's profile picture"""
        try:
            url = f'{self.base_url}/people/~'
            params = {
                'projection': '(profilePicture(displayImage~:playableStreams))'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'profilePicture' in data and 'displayImage~' in data['profilePicture']:
                elements = data['profilePicture']['displayImage~'].get('elements', [])
                if elements:
                    return elements[0]['identifiers'][0]['identifier']
            
            return None
            
        except requests.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
    
    def post_share(self, text, visibility='PUBLIC'):
        """Post a share to LinkedIn"""
        try:
            url = f'{self.base_url}/shares'
            
            data = {
                'content': {
                    'contentEntities': [],
                    'title': text
                },
                'distribution': {
                    'linkedInDistributionTarget': {}
                },
                'owner': 'urn:li:person:' + self.get_profile().get('id', ''),
                'subject': text,
                'text': {
                    'text': text
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            return {'error': f'API request failed: {str(e)}'}
