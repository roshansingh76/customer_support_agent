from fastapi import APIRouter, HTTPException, status

from ..models.user_model import User
from ..repositories.user_repositories import UserRepository
from ..schemas.user_schema import Token, UserCreate, UserLogin, UserOut
from db.session import DbSession
from ..services.security import create_access_token, password_hash

router = APIRouter()


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def check_login(data: UserLogin, db: DbSession) -> Token:
    user = User(
        email=str(data.email),
        password_hash=data.password,
    )
    result = await UserRepository(db).authenticate(user)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=await create_access_token(result.email))


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, db: DbSession) -> UserOut:
    user = User(
        name=data.name,
        email=str(data.email),
        password_hash=await password_hash(data.password),
    )
    return await UserRepository(db).create(user)
