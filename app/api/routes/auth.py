import fastapi
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_auth_service
from app.db.session import get_db
from app.schemas.user import Token, UserCreate, UserRead
from app.services.auth import AuthService

router = fastapi.APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=fastapi.status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = fastapi.Depends(get_db)):
    auth_service = AuthService(db)
    existing = auth_service.get_user_by_email(user.email)
    if existing:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    created = auth_service.create_user(user.email, user.password)
    return created


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = fastapi.Depends(),
    auth_service: AuthService = fastapi.Depends(get_auth_service),
):
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = auth_service.create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)
