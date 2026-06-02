from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from ..database import get_collection
from ..models.user import UserCreate, UserLogin, UserResponse, Token
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    """Register a new user account."""
    collection = get_collection("users")

    # Check if email already exists
    existing = await collection.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create user document
    import uuid
    user_doc = {
        "user_id": str(uuid.uuid4()),
        "email": user_data.email,
        "hashed_password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }

    await collection.insert_one(user_doc)

    return UserResponse(
        user_id=user_doc["user_id"],
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
    )


@router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and receive a JWT access token."""
    collection = get_collection("users")

    user = await collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token({"sub": user["user_id"], "email": user["email"]})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse(
            user_id=user["user_id"],
            email=user["email"],
            full_name=user.get("full_name"),
        ),
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_me(token: str = None):
    """Get current authenticated user profile."""
    from ..auth import decode_token
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    collection = get_collection("users")
    user = await collection.find_one({"user_id": payload["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        full_name=user.get("full_name"),
    )
