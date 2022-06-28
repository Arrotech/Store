from flask import url_for, current_app
from itsdangerous import URLSafeTimedSerializer


def default_encode_token(email, salt='email-confirm-key'):
    """Encode token using email."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=salt)


def default_decode_token(token, salt='email-confirm-key', expiration=3600):
    """Decode token and get the email."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token, salt=salt, max_age=expiration)
        return email
    except Exception:
        return False


def generate_url(endpoint, token):
    """Generate url to concatenate at the end of another url."""
    return url_for(endpoint, token=token, _external=True)
