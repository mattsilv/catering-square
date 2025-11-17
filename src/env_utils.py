"""
Purpose: Environment variable utilities for flexible sandbox/production switching
Related: All scripts that interact with Square API
Refactor if: Supporting more than 2 environments OR complex credential logic
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def get_environment():
    """Get the active environment (sandbox or production)"""
    return os.getenv('SQUARE_ENVIRONMENT', 'sandbox').lower()


def get_access_token():
    """Get access token for active environment"""
    env = get_environment()

    if env == 'production':
        token = os.getenv('PRODUCTION_ACCESS_TOKEN')
        if not token:
            raise ValueError("PRODUCTION_ACCESS_TOKEN not found in .env file")
        return token
    else:
        token = os.getenv('SANDBOX_ACCESS_TOKEN')
        if not token:
            raise ValueError("SANDBOX_ACCESS_TOKEN not found in .env file")
        return token


def get_app_id():
    """Get app ID for active environment"""
    env = get_environment()

    if env == 'production':
        return os.getenv('PRODUCTION_APP_ID')
    else:
        return os.getenv('SANDBOX_APP_ID')


def get_main_location_id():
    """Get main location ID for active environment"""
    env = get_environment()

    if env == 'production':
        location_id = os.getenv('PRODUCTION_LOCATION_MAIN')
        if not location_id:
            raise ValueError("PRODUCTION_LOCATION_MAIN not found in .env file")
        return location_id
    else:
        location_id = os.getenv('SANDBOX_LOCATION_MAIN')
        if not location_id:
            raise ValueError("SANDBOX_LOCATION_MAIN not found in .env file")
        return location_id


def is_production():
    """Check if currently in production environment"""
    return get_environment() == 'production'


def is_sandbox():
    """Check if currently in sandbox environment"""
    return get_environment() == 'sandbox'


def get_dashboard_url(path=''):
    """Get Square Dashboard URL for active environment"""
    if is_production():
        base = 'https://squareup.com/dashboard'
    else:
        base = 'https://app.squareupsandbox.com/dashboard'

    if path:
        return f"{base}/{path.lstrip('/')}"
    return base


def print_environment_info():
    """Print current environment configuration"""
    env = get_environment()

    print("=" * 70)
    print(f"🔧 ENVIRONMENT: {env.upper()}")
    print("=" * 70)

    try:
        token = get_access_token()
        token_preview = f"{token[:10]}...{token[-10:]}" if len(token) > 20 else "***"
        print(f"Access Token: {token_preview}")
    except ValueError as e:
        print(f"⚠️  Access Token: {e}")

    try:
        location_id = get_main_location_id()
        print(f"Main Location ID: {location_id}")
    except ValueError as e:
        print(f"⚠️  Main Location ID: {e}")

    print(f"Dashboard: {get_dashboard_url()}")
    print()

    if is_production():
        print("⚠️  WARNING: PRODUCTION MODE - Changes affect live data!")
        print("=" * 70)
        print()


# Backward compatibility: Set legacy environment variables
# This ensures old scripts still work
def set_legacy_env_vars():
    """Set legacy SQUARE_ACCESS_TOKEN for backward compatibility"""
    try:
        os.environ['SQUARE_ACCESS_TOKEN'] = get_access_token()
        os.environ['SQUARE_LOCATION_ID'] = get_main_location_id()
    except ValueError:
        pass  # Variables not set yet


# Auto-set legacy vars on import
set_legacy_env_vars()


if __name__ == "__main__":
    # Test/display environment info
    print_environment_info()
