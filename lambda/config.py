"""
Configuration loader for Open Bank Project API credentials
Loads from .env file (make sure it's in .cursorignore)
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Simple config class to load OBP credentials from .env"""
    
    OBP_BASE_URL = os.getenv('OBP_BASE_URL')
    OBP_API_VERSION = os.getenv('OBP_API_VERSION')
    OBP_CONSUMER_ID = os.getenv('OBP_CONSUMER_ID')
    OBP_USERNAME = os.getenv('OBP_USERNAME')
    OBP_PASSWORD = os.getenv('OBP_PASSWORD')
    OBP_CONSUMER_KEY = os.getenv('OBP_CONSUMER_KEY')
    OBP_CONSUMER_SECRET = os.getenv('OBP_CONSUMER_SECRET')
    OBP_DIRECTLOGIN_ENDPOINT = os.getenv('OBP_DIRECTLOGIN_ENDPOINT')
    
    # OAuth2 credentials (if needed)
    OAUTH2_CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
    OAUTH2_REDIRECT_URI = os.getenv('OAUTH2_REDIRECT_URI')
    OAUTH2_CLIENT_SCOPE = os.getenv('OAUTH2_CLIENT_SCOPE')
    OAUTH2_JWS_ALG = os.getenv('OAUTH2_JWS_ALG')
    OAUTH2_JWK_PRIVATE_KEY = os.getenv('OAUTH2_JWK_PRIVATE_KEY')
    
    @classmethod
    def validate_directlogin(cls):
        """Validate that required DirectLogin credentials are present"""
        required = ['OBP_USERNAME', 'OBP_PASSWORD', 'OBP_CONSUMER_KEY', 'OBP_DIRECTLOGIN_ENDPOINT']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required credentials: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def validate_oauth2(cls):
        """Validate that required OAuth2 credentials are present"""
        required = ['OAUTH2_CLIENT_ID', 'OAUTH2_REDIRECT_URI', 'OAUTH2_CLIENT_SCOPE']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required OAuth2 credentials: {', '.join(missing)}")
        
        return True

