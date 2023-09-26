import secrets


def generate_token(length=64) -> str:
    return secrets.token_urlsafe(length)
