# auth.py
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import PyJWTError

from config import (
    GOOGLE_CLIENT_ID,
    AIA_JWT_SECRET,
    AIA_JWT_ALGORITHM,
    AIA_JWT_EXP_HOURS,
)


class AuthError(Exception):
    pass


def verify_google_credential(credential: str):
    try:
        payload = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return payload
    except Exception as e:
        raise AuthError(f"Erro ao validar token Google: {str(e)}")


def create_aia_token(google_payload: dict):
    expires = datetime.utcnow() + timedelta(hours=AIA_JWT_EXP_HOURS)

    payload = {
        "sub": google_payload["sub"],
        "email": google_payload.get("email"),
        "name": google_payload.get("name"),
        "exp": expires,
    }

    return jwt.encode(payload, AIA_JWT_SECRET, algorithm=AIA_JWT_ALGORITHM)


def decode_aia_token(token: str):
    try:
        return jwt.decode(
            token,
            AIA_JWT_SECRET,
            algorithms=[AIA_JWT_ALGORITHM]
        )
    except PyJWTError as e:
        raise AuthError(f"Token inválido: {str(e)}")
