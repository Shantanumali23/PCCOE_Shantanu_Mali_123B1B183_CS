"""
CodeSecure AI — Authentication API Endpoints
Handles user registration, authentication, JWT token issuance, and identity verification.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from app.utils.fastapi_compat import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from app.db import get_db, SQLALCHEMY_AVAILABLE
from app.models import User
from app.schemas import TokenResponse, UserCreate, UserLogin, UserResponse
from app.security.authentication import create_access_token, hash_password, verify_access_token, verify_password
from app.services.security_service import security_service
from app.utils.logging_utils import get_logger

logger = get_logger("auth_api")
router = APIRouter(prefix="/auth", tags=["Authentication"])
security_scheme = HTTPBearer(auto_error=False)

# In-memory users store for fallback/test environments
IN_MEMORY_USERS: Dict[str, Dict[str, Any]] = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": hash_password("Admin@CodeSecure2026"),
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
    },
    "reviewer": {
        "id": 2,
        "username": "reviewer",
        "password_hash": hash_password("Reviewer@CodeSecure2026"),
        "role": "reviewer",
        "created_at": datetime.now(timezone.utc),
    },
    "developer": {
        "id": 3,
        "username": "developer",
        "password_hash": hash_password("Dev@CodeSecure2026"),
        "role": "developer",
        "created_at": datetime.now(timezone.utc),
    },
    "security_eng": {
        "id": 4,
        "username": "security_eng",
        "password_hash": hash_password("SecEng@CodeSecure2026"),
        "role": "security_engineer",
        "created_at": datetime.now(timezone.utc),
    },
}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> Dict[str, Any]:
    """Dependency for extracting and validating the current authenticated user from Bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject.")

    # Search in DB or in-memory
    if SQLALCHEMY_AVAILABLE:
        try:
            from app.db import SessionLocal
            if SessionLocal:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        return {"id": user.id, "username": user.username, "role": user.role}
                finally:
                    db.close()
        except Exception:
            pass

    if username in IN_MEMORY_USERS:
        u = IN_MEMORY_USERS[username]
        return {"id": u["id"], "username": u["username"], "role": u["role"]}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account not found.")


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db=Depends(get_db)):
    """Registers a new user account."""
    username = user_data.username.strip()
    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    role = user_data.role.lower()
    if role not in ("developer", "reviewer", "security_engineer", "admin"):
        role = "developer"

    # Check existence
    if username in IN_MEMORY_USERS:
        raise HTTPException(status_code=400, detail="Username already exists.")

    hashed = hash_password(user_data.password)
    user_id = len(IN_MEMORY_USERS) + 1
    now = datetime.now(timezone.utc)

    if SQLALCHEMY_AVAILABLE and db:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists.")
        new_user = User(username=username, password_hash=hashed, role=role, created_at=now)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_id = new_user.id

    IN_MEMORY_USERS[username] = {
        "id": user_id,
        "username": username,
        "password_hash": hashed,
        "role": role,
        "created_at": now,
    }

    security_service.log_event(
        action="USER_REGISTERED",
        resource=f"user:{username}",
        user_id=user_id,
        username=username,
        details=f"AssignedRole={role}",
    )

    return UserResponse(id=user_id, username=username, role=role, created_at=now)


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db=Depends(get_db)):
    """Authenticates credentials and returns a signed JWT token."""
    username = login_data.username.strip()
    user_record = None

    if SQLALCHEMY_AVAILABLE and db:
        try:
            db_user = db.query(User).filter(User.username == username).first()
            if db_user:
                user_record = {
                    "id": db_user.id,
                    "username": db_user.username,
                    "password_hash": db_user.password_hash,
                    "role": db_user.role,
                    "created_at": db_user.created_at,
                }
        except Exception:
            pass

    if not user_record and username in IN_MEMORY_USERS:
        user_record = IN_MEMORY_USERS[username]

    if not user_record or not verify_password(login_data.password, user_record["password_hash"]):
        security_service.log_event(
            action="LOGIN_FAILED",
            resource=f"user:{username}",
            status="FAILURE",
            username=username,
            details="Invalid username or password.",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    # Issue access token
    token = create_access_token({"sub": user_record["username"], "role": user_record["role"], "id": user_record["id"]})

    security_service.log_event(
        action="LOGIN_SUCCESS",
        resource=f"user:{username}",
        status="SUCCESS",
        user_id=user_record["id"],
        username=username,
        details=f"Role={user_record['role']}",
    )

    user_resp = UserResponse(
        id=user_record["id"],
        username=user_record["username"],
        role=user_record["role"],
        created_at=user_record.get("created_at"),
    )
    return TokenResponse(access_token=token, token_type="bearer", user=user_resp)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Returns profile for currently authenticated user."""
    return UserResponse(
        id=user["id"],
        username=user["username"],
        role=user["role"],
    )
