import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# SECURITY CONFIGURATION
# =========================================================

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD"
)


# =========================================================
# VALIDATE REQUIRED CONFIGURATION
# =========================================================

if not SECRET_KEY:

    raise RuntimeError(
        "JWT_SECRET_KEY is not configured in .env"
    )


if not ADMIN_USERNAME:

    raise RuntimeError(
        "ADMIN_USERNAME is not configured in .env"
    )


if not ADMIN_PASSWORD:

    raise RuntimeError(
        "ADMIN_PASSWORD is not configured in .env"
    )


# =========================================================
# CREATE ACCESS TOKEN
# =========================================================

def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# =========================================================
# VERIFY ACCESS TOKEN
# =========================================================

def verify_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get(
            "sub"
        )

        if not username:

            return None

        return username

    except JWTError:

        return None