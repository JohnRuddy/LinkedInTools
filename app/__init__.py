from flask import Flask
from flask_session import Session
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='../templates')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # LinkedIn OAuth Configuration
    app.config['LINKEDIN_CLIENT_ID'] = os.environ.get('LINKEDIN_CLIENT_ID')
    app.config['LINKEDIN_CLIENT_SECRET'] = os.environ.get('LINKEDIN_CLIENT_SECRET')
    app.config['LINKEDIN_REDIRECT_URI'] = os.environ.get('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/auth/linkedin/callback')
    
    # Initialize extensions
    Session(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    return app
