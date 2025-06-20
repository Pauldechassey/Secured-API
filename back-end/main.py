from fastapi import FastAPI, Body, status, Request, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from urllib.parse import urlparse, parse_qs, ParseResult
from typing import Optional, Dict, List
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from passlib.context import CryptContext
import re
import os
from sqlalchemy.exc import SQLAlchemyError

# CSP
from starlette.middleware.base import BaseHTTPMiddleware

# bdd
from sqlalchemy.orm import Session
from db import engine, Base, get_db
from models import ParsedURL, User
from auth import create_access_token

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://localhost:8443",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


ok_Stat = status.HTTP_200_OK
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        env = os.getenv("APP_ENV", "development")
        if env == "production":
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'none'; "
            )
        else:
            response.headers["Content-Security-Policy"] = (
                ""
            )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response


# --- Pydantic Models ---
class URLParseRequest(BaseModel):
    url: str = Field(
        ...,
        example="https://www.example.com:8080/path?param=value#section",
        description="A valid URL to parse"
    )

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "url": "https://www.google.com/search?q=fastapi"
                },
                {
                    "url": "https://api.github.com:443/repos/username/repo"
                }
            ]
        }


class URLParseResponse(BaseModel):
    original_url: str
    scheme: Optional[str] = None
    netloc: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    query_string: Optional[str] = None
    query_params: Optional[Dict[str, List[str]]] = None
    fragment: Optional[str] = None


# Configuration
SECRET_KEY = "votre_clé_secrète"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class UserCreate(BaseModel):
    email: str = Field(..., example="test@example.com")
    password: str = Field(..., example="TestPass123!")
    fullname: str = Field(..., example="Test User")


class PasswordStrengthResponse(BaseModel):
    password: str
    strength: str
    score: int
    suggestions: list[str] = []


class PasswordInput(BaseModel):
    password: str = Field(..., min_length=1, description="Password to check")


# --- Business Logic ---
def parse_url_components(url_to_parse: str) -> URLParseResponse:
    """
    Parses a given URL string into its components.
    STUDENTS TO COMPLETE THIS FUNCTION.
    """
    # TODO 1: Use `urllib.parse.urlparse()` on the `url_to_parse` string.
    #         This will return a `ParseResult` object (typically a named tuple)
    #         Store this result in a variable (e.g., `parsed_result`)
    # Example: parsed_result: ParseResult = urlparse(url_to_parse)
    parsed_result: ParseResult = urlparse(url_to_parse)

    # TODO 2: Extract individual components from `parsed_result`.
    #     - scheme (e.g., `parsed_result.scheme`)
    #     - netloc (e.g., `parsed_result.netloc`)
    #     - path (e.g., `parsed_result.path`)
    #     - query (this is the raw query string, e.g., `parsed_result.query`)
    #     - fragment (e.g., `parsed_result.fragment`)

    scheme = parsed_result.scheme
    netloc = parsed_result.netloc
    path = parsed_result.path
    raw_query_str = parsed_result.query
    fragment = parsed_result.fragment

    # TODO 3: Extract hostname and port from the `netloc`.
    #          The `parsed_result` object (from `urlparse`)
    #          has `.hostname` and `.port` attributes
    #          that are convenient for this. They can be `None`
    #          Store them in `hostname_val` and `port_val`.
    hostname_val = parsed_result.hostname
    port_val = parsed_result.port

    # TODO 4:
    #  Parse the `raw_query_string` into a dictionary of query parameters.
    #  Use `urllib.parse.parse_qs(raw_query_string)`.
    #  This function returns a dictionary where keys are parameter names
    #  and values are lists of strings
    # (as a parameter can appear multiple times)
    #  Store this in `parsed_query_params`. If `raw_query_string` is empty,
    #  `parse_qs` will return an empty dictionary, which is fine.
    parsed_query_params = parse_qs(raw_query_str) if raw_query_str else {}

    return URLParseResponse(
        original_url=url_to_parse,
        scheme=scheme,
        netloc=netloc,
        hostname=hostname_val,
        port=port_val,
        path=path,
        query_string=raw_query_str if raw_query_str else None,
        query_params=parsed_query_params if parsed_query_params else None,
        fragment=fragment if fragment else None
    )


def check_password_strength(password: str) -> PasswordStrengthResponse:
    """Analyzes the password and returns its strength and suggestions."""
    MAX_PASSWORD_LENGTH = 50
    MIN_PASSWORD_LENGTH = 8

    if len(password) > MAX_PASSWORD_LENGTH:
        return PasswordStrengthResponse(
            password=password[:10] + "...",
            strength="invalid",
            score=0,
            suggestions=[
                "Password is too long. Maximum length is "
                f"{MAX_PASSWORD_LENGTH} characters."
            ]
        )

    if len(password) < MIN_PASSWORD_LENGTH:
        return PasswordStrengthResponse(
            password=password,
            strength="very_weak",
            score=0,
            suggestions=[
                f"Password must be at least "
                f"{MIN_PASSWORD_LENGTH} characters long.",
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            ]
        )

    strength_levels = {
        0: "very_weak",
        1: "weak",
        2: "medium",
        3: "strong",
        4: "very_strong"
    }
    score = 0
    suggestions = []

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_symbol = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

    if not has_upper:
        suggestions.append("Add at least one uppercase letter.")
    if not has_lower:
        suggestions.append("Add at least one lowercase letter.")
    if not has_digit:
        suggestions.append("Add at least one number.")
    if not has_symbol:
        suggestions.append("Add at least one special character (e.g., !@#$%).")

    if len(password) < 8:
        final_score = 0
        if not any("at least 8 characters" in s for s in suggestions):
            suggestions.append(
                "Password should be at least 8 characters long."
                )
    elif len(password) == 8:
        if sum([has_upper, has_lower, has_digit, has_symbol]) == 4:
            final_score = 4
            score = 4
        else:
            final_score = min(2, score)
    elif len(password) < 10:
        final_score = min(2, score)
    else:
        score = sum([has_upper, has_lower, has_digit, has_symbol])
        if len(password) >= 12:
            score += 1
        final_score = min(score, max(strength_levels.keys()))

    if sum([has_upper, has_lower, has_digit, has_symbol]) <= 2:
        final_score = 1

    strength_category = strength_levels[final_score]

    return PasswordStrengthResponse(
        password=password,
        strength=strength_category,
        score=final_score,
        suggestions=suggestions
    )


def is_valid_url(url: str) -> bool:
    """
    Validate URL according to RFC specifications:
    - Must start with http:// or https://
    - Domain must follow DNS naming conventions
    - No underscores in domain
    - Valid characters in path
    """
    url_pattern = re.compile(
        r'^(?:(?:https?|ftp|mailto)://)?'
        r'(?:'
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'[^@\s]+@[^@\s]+\.[^@\s]+|'
        r'[A-Z0-9.-]+@[A-Z0-9.-]+'
        r')'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)?$', re.IGNORECASE)

    if url.startswith('mailto:'):
        email_part = url[7:]
        return '@' in email_part and '.' in email_part.split('@')[1]

    return bool(url_pattern.match(url))


def is_valid_email(email: str) -> bool:
    """
    Validate email format using regex.
    Basic validation for:
    - Must contain @ and .
    - Local part must be 1-64 characters
    - Domain part must be 1-255 characters
    - Valid characters in local and domain parts
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False

    local_part = email.split('@')[0]
    domain_part = email.split('@')[1]

    if len(local_part) > 64 or len(domain_part) > 255:
        return False

    return True


# --- API Endpoints ---


@app.post("/parse_url", response_model=URLParseResponse)
@limiter.limit("120/minute")
async def parse_url(
    request: Request,
    payload: URLParseRequest = Body(...),
    db: Session = Depends(get_db),
):
    try:
        url_str = payload.url
        ex_API = "https://api.github.com:443/repos/user/repo"
        error_Char = "Domain must contain valid characters (a-z, 0-9, hyphen)"
        if not is_valid_url(url_str):
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Invalid URL format",
                    "error": "URL must follow these rules:",
                    "rules": [
                        "Must start with http:// or https://",
                        "Domain must be valid (no underscores)",
                        error_Char,
                        "Must have a valid TLD"
                    ],
                    "examples": [
                        "https://www.example.com",
                        ex_API,
                        "http://localhost:8000/api"
                    ]
                }
            )

        parsed = urlparse(url_str)

        if '_' in parsed.netloc:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid domain name",
                    "error": "Domain names cannot contain underscores",
                    "provided": parsed.netloc,
                    "example": "Use hyphens instead: my-domain.com"
                }
            )

        parsed_data = parse_url_components(url_str)
        new_url = ParsedURL(
            original_url=parsed_data.original_url,
            scheme=parsed_data.scheme,
            netloc=parsed_data.netloc,
            hostname=parsed_data.hostname,
            port=parsed_data.port,
            path=parsed_data.path,
            query_string=parsed_data.query_string,
            fragment=parsed_data.fragment
        )
        db.add(new_url)
        db.commit()
        db.refresh(new_url)
        return parsed_data

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid URL",
                "error": str(e),
                "examples": [
                    "https://www.example.com",
                    "https://api.github.com:443/repos/user/repo",
                    "http://localhost:8000/api"
                ]
            }
        )


@app.get("/health_url_parser")
async def health_check_url_parser():
    return {"status_url_parser": "ok"}


@app.post("/is_secure")
async def is_secure_endpoint(
    request: Request,
    payload: URLParseRequest = Body(...)
):
    parsed = urlparse(str(payload.url))
    return {"is_secure": parsed.scheme.lower() == "https"}


@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    MAX_PASSWORD_LENGTH = 50
    if len(user.password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Password too long",
                "error": (
                    f"Password must be less than "
                    f"{MAX_PASSWORD_LENGTH} characters"
                ),
                "current_length": len(user.password)
            }
        )

    if not is_valid_email(user.email):
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid email format",
                "error": "Please provide a valid email address",
                "examples": [
                    "user@example.com",
                    "firstname.lastname@company.com"
                ]
            }
        )

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    password_check = check_password_strength(user.password)
    if password_check.strength == "invalid":
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid password",
                "error": password_check.suggestions[0]
            }
        )
    elif password_check.score < 3:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Password not strong enough",
                "strength": password_check.strength,
                "suggestions": password_check.suggestions
            }
        )

    sanitized_email = re.sub(r'[;<>&]', '', user.email)
    sanitized_fullname = re.sub(r'[;<>&]', '', user.fullname)

    if len(sanitized_fullname) > 100 or len(sanitized_email) > 255:
        raise HTTPException(
            status_code=400,
            detail="Input length exceeds maximum allowed"
        )

    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=sanitized_email,
        fullname=sanitized_fullname,
        hashed_password=hashed_password
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )

    return {"message": "User created successfully"}


@app.post("/login", response_model=dict)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):
    print(f"Tentative de connexion pour : {form_data.username}")
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        print("Utilisateur non trouvé")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not pwd_context.verify(form_data.password, user.hashed_password):
        print(f"Mot de passe incorrect pour {user.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    print(f"Connexion réussie pour {user.email}")
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post(
    "/check_password_strength",
    response_model=PasswordStrengthResponse,
    status_code=status.HTTP_200_OK
)
async def check_password_strength_endpoint(payload: PasswordInput = Body(...)):
    """Receives a password and returns an analysis of its strength."""
    analysis_result = check_password_strength(payload.password)
    return analysis_result


@app.get("/health_strength_checker")
async def health_check_strength_checker():
    """Health check for the Password Strength Checker API."""
    return {"status_strength_checker": "ok"}


app.add_middleware(CSPMiddleware)

# For running with `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000,
                ssl_keyfile="key.pem",
                ssl_certfile="cert.pem")
    # uvicorn.run(app, host="0.0.0.0", port=8000) pour enlever l'alerte bandit,
    # on fait en local
