from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.all_models import User
from app.schemas.all_schemas import Token, LoginRequest, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        # For development/demo convenience, return or create a default inspector if no token passed
        default_user = db.query(User).filter(User.email == "inspector@gov.in").first()
        if not default_user:
            default_user = User(
                email="inspector@gov.in",
                full_name="Senior Legal Metrology Inspector",
                hashed_password=get_password_hash("inspector123"),
                role="INSPECTOR",
                badge_number="LM-DL-8821"
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
        return default_user

    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials"
        )
    
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # If demo user, auto-create for convenience
        if req.email in ["inspector@gov.in", "supervisor@gov.in", "admin@gov.in"]:
            role = "SUPERVISOR" if "supervisor" in req.email else ("ADMIN" if "admin" in req.email else "INSPECTOR")
            user = User(
                email=req.email,
                full_name=f"Legal Metrology {role.capitalize()}",
                hashed_password=get_password_hash(req.password),
                role=role,
                badge_number="LM-IND-01"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "badge_number": user.badge_number
        }
    }

@router.post("/register", response_model=UserResponse)
def register(req: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user = User(
        email=req.email,
        full_name=req.full_name,
        hashed_password=get_password_hash(req.password),
        role=req.role,
        badge_number=req.badge_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
