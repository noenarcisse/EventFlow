from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import AvatarUpdate, PasswordChange, ProfileUpdate, Token, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.email))


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current


MAX_AVATAR_CHARS = 2_000_000  # ~1.5 MB en base64


@router.patch("/me", response_model=UserOut)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    data = payload.model_dump(exclude_unset=True)
    # L'email et le role ne sont volontairement pas modifiables ici.
    for field in ("full_name", "phone"):
        if field in data and data[field] is not None:
            setattr(current, field, data[field])
    db.commit()
    db.refresh(current)
    return current


@router.post("/me/avatar", response_model=UserOut)
def update_avatar(
    payload: AvatarUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    avatar = payload.avatar.strip()
    if not avatar.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="Image invalide (format data URL attendu)")
    if len(avatar) > MAX_AVATAR_CHARS:
        raise HTTPException(status_code=413, detail="Image trop volumineuse (max ~1.5 Mo)")
    current.avatar = avatar
    db.commit()
    db.refresh(current)
    return current


@router.delete("/me/avatar", response_model=UserOut)
def remove_avatar(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    current.avatar = None
    db.commit()
    db.refresh(current)
    return current


@router.post("/change-password", status_code=204)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current.password_hash):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    if len(payload.new_password) < 8:
        raise HTTPException(status_code=400, detail="Le nouveau mot de passe doit faire au moins 8 caracteres")
    current.password_hash = hash_password(payload.new_password)
    db.commit()
