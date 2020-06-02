from datetime import datetime, timedelta
import logging

import jwt  # json web tokens

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# starlette HTTPException doesn't work with headers= {} keyword arg
# from starlette.exceptions import HTTPException

from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from starlette.responses import Response, JSONResponse

# create context to hash and verify passwords
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.models.player import Player, PlayerBase
from app.models import user as _user, token as _token
from app.game_logic.user import User
from app.database import crud, db_models
from app.database.database import SessionLocal, engine

# cookie authorization
from app.api.oauth2withcookies import OAuth2PasswordBearerCookie

from app.config import SECRET_KEY, JWT_ENCODE_ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS,
                        COOKIE_DOMAIN

# logger = logging.getLogger('backend')

# define the authentication router that is imported in main
router = APIRouter()

# password context needed to hash and verify passwords
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# O authentification scheme 2 that is injected as a dependency
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl='/token')

# bind the database models for the table 'users'
db_models.Base.metadata.create_all(bind=engine)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, username: str, password: str):
    """
    Tries to get the user from the database and verifies the supplied password
    with the stored hashed one. 
    Returns: 
    the user if the user exists and was verified
    False, otherwise
    """
    password
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_db():
    """
    Function that 'yields' a database session for CRUD operations. Fastapi
    resolves this session as a dependency that injects the database session
    into functions that need it. 
    """
    db = SessionLocal()
    try:
        # need python >3.6 for the yield dependency to work, see the fastapi
        # docs for a backport
        yield db
    finally:
        # make sure the database closes even if there was an exception
        db.close()


""" 
Implement the authentication using json web tokens:
Upon login, the users credentials are verified against the sqlite database
and if successful, the user obtains a access token that is valid an hour. 
After an hour he has to log back in. 
"""


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire})

    # this creates a bytestring, need to decode it to obtain a string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ENCODE_ALGORITHM)

    return encoded_jwt.decode('utf-8')


def get_user(db, username: str) -> _user.UserInDB:
    user = crud.get_user_by_username(db, username)
    return user


async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)):
    # predefine the exception
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    logging.debug(f'Obtained token {token}')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = _token.TokenData(username=username)
    except jwt.PyJWTError:
        logging.warn('PyJWTError')
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# -----------------------------------------------------------------------------
# Paths:


@router.get('/users/me')
async def read_users_me(current_user: _user.User = Depends(get_current_user)):
    logging.info('try to get user')
    return current_user


@router.get('/tokens')
async def read_tokens(token: str = Depends(oauth2_scheme)):
    return {'token': token}


@router.get('/test')
def test():
    pass


@router.post("/token", response_model=_token.Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # cookies are set automatically by fastapi
    response.set_cookie(
        key='Authorization',
        value=f'Bearer {access_token}',
        path='/',
        domain=COOKIE_DOMAIN,
        # domain='localtest.me',
        httponly=True,
        secure=False,
        # samesite='none'
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/create_user', response_model=_user.User)
async def create_user(
        new_user: _user.UserCreate,
        db: Session = Depends(get_db)):
    # user contains username (str) and password (str)
    if not new_user.username:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Invalid username'
        )

    # check for duplicate names
    db_user = crud.get_user_by_username(db, new_user.username)
    if db_user:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail='Username already exists'
        )

    # the user containing the ID generated by the database is returned
    user_in_db = crud.create_user(db, new_user)


@router.get('/logout')
async def logout_user(response : Response):
    response.delete_cookie('Authorization', domain='localtest.me')
    
