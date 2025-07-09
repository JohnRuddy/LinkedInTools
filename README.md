/bin/linkedin_bot/README.md
# LinkedIn Bot

A Flask web application that allows users to authenticate with LinkedIn and view their profile information.

## Features

- LinkedIn OAuth 2.0 authentication
- Display user profile information
- Responsive web interface
- Session management
- Error handling and flash messages

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a LinkedIn app at https://developer.linkedin.com/
   - Set redirect URI to: `http://localhost:5000/auth/linkedin/callback`

3. Configure environment variables in `.env`:
```
SECRET_KEY=your-secret-key-here
LINKEDIN_CLIENT_ID=your-linkedin-client-id
LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
LINKEDIN_REDIRECT_URI=http://localhost:5000/auth/linkedin/callback
```

4. Run the application:
```bash
python run.py
```

5. Visit `http://localhost:5000` in your browser

## Project Structure

```
linkedin_bot/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   └── linkedin_api.py
├── templates/
│   ├── base.html
│   └── index.html
├── run.py
├── config.py
├── requirements.txt
├── .env
└── README.md
```

## API Endpoints

- `/` - Main page (login or profile)
- `/auth/linkedin` - Initiate LinkedIn OAuth
- `/auth/linkedin/callback` - OAuth callback
- `/refresh` - Refresh profile data
- `/logout` - Logout user

## LinkedIn API Permissions

The app requests the following LinkedIn API scopes:
- `r_liteprofile` - Basic profile information
- `r_emailaddress` - Email address
- `w_member_social` - Post updates (for future features)