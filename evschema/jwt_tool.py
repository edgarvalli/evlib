import jwt
from flask import current_app
from datetime import datetime, timedelta


def access_token(payload: dict) -> str:
    # Verificar si el campo 'exp' ya existe en el payload
    if "exp" not in payload:
        # Establecer la expiración a 1 día (24 horas) a partir de ahora
        payload["exp"] = datetime.now() + timedelta(days=1)

    # Obtener la clave secreta para el Access Token
    jwtpass: str = current_app.config["JWT_SECRET_KEY"]

    # Generar el Access Token
    return jwt.encode(payload, jwtpass, algorithm="HS256")


def refresh_token(payload: dict) -> str:
    # Verificar si el campo 'exp' ya existe en el payload
    if "exp" not in payload:
        # Establecer la expiración a 7 días a partir de ahora
        payload["exp"] = datetime.now() + timedelta(days=7)

    # Obtener la clave secreta para el Refresh Token
    jwtpass: str = current_app.config["JWT_REFRESH_SECRET_KEY"]

    # Generar el Refresh Token
    return jwt.encode(payload, jwtpass, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        # La clave secreta debe ser la misma con la que firmaste el token
        jwtpass: str = current_app.config["JWT_SECRET_KEY"]

        # Decodificar el token (automáticamente verifica la firma y la expiración)
        decoded = jwt.decode(token, jwtpass, algorithms=["HS256"])

        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": True, "message": "El token ha expirado"}
    except jwt.InvalidTokenError:
        return {"error": True, "message": "Token invalido"}


def decode_refresh_token(token: str) -> dict:
    try:
        # La clave secreta debe ser la misma con la que firmaste el token
        jwtpass: str = current_app.config["JWT_REFRESH_SECRET_KEY"]

        # Decodificar el token (automáticamente verifica la firma y la expiración)
        decoded = jwt.decode(token, jwtpass, algorithms=["HS256"])

        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": True, "message": "El token ha expirado"}
    except jwt.InvalidTokenError:
        return {"error": True, "message": "Token invalido"}
