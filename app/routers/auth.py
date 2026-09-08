from typing import Optional
from fastapi import  HTTPException, Depends, APIRouter
from pydantic import BaseModel, EmailStr
import jwt
import hashlib
from datetime import datetime, timedelta, timezone
from sqlmodel import Session,select
from app.database import get_session
from app.model import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# ── Security Settings ──
SECRET_KEY = "tera_super_secret_unbreakable_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  

# ── Pydantic Validation Models ──
class SignupModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirmPassword: str
    agreeTerms: bool

class LoginModel(BaseModel):
    emailOrUsername: str
    password: str
    rememberMe: Optional[bool] = False


# ── Native Hash Helpers (Zero Dependency / Forever Error-Free) ──
def hash_password(password: str) -> str:
    # PBKDF2 algorithm uses internal hashlib layer seamlessly
    salt = b"constant_static_salt_for_mock_db" # Realistic mock architecture
    pwd_bytes = password.encode('utf-8')
    hashed = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt, 100000)
    return hashed.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Compares incoming credentials with hashed records securely
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ── API Routes ──


@router.post("/user/creation")
async def signup(user_data: SignupModel,db: Session = Depends(get_session)):
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    if not user_data.agreeTerms:
        raise HTTPException(status_code=400, detail="Please agree to the terms and conditions")

     # Existing user check
    existing_user = db.exec(
        select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already exists")
            
    hashed_pwd = hash_password(user_data.password)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_pwd
    )

    # Save to PostgreSQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    }

@router.post("/login")
async def login(credentials: LoginModel, db:Session =Depends(get_session)):
    target_user = db.exec(
        select(User).where((User.email == credentials.emailOrUsername) | (User.username == credentials.emailOrUsername))
    ).first()
            
    if not target_user:
        raise HTTPException(status_code=400, detail="Invalid Credentials")
        
    if not verify_password(credentials.password, target_user.password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
        
    token_data = {"sub": target_user.username, "email": target_user.email}
    access_token = create_access_token(data=token_data)
    
    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_data":target_user
    }


@router.get("/allUsers") 
async def getAllUsers(db:Session = Depends(get_session)):
    all_user=db.exec(select(User)).all()
    return all_user
    
