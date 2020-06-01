from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import random
import string

from fastapi import APIRouter

from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from app.models.player import Player, PlayerBase
from app.game_logic.user import User

# TEST
from fastapi import Depends
from sqlalchemy.orm import Session

from ..database import db_models, crud
from ..database.database import SessionLocal, engine

# db_models.Base.metadata.create_all(bind=engine)

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')

# TEST DATABASE


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# fake_users_db = {
#     'john': {
#         'id': 12,
#         'name': 'john',
#         'hashed_password': 'safepassword',
#         'is_active': False,
#         'current_game': None,
#     },
#     'alice': {
#         'id': 12,
#         'name': 'john',
#         'hashed_password': 'safepassword',
#         'is_active': False,
#         'current_game': None,
#     }
# }


# def get_user(db, name: str):
#     if name in db:
#         user_dict = db[name]
#         return UserInDB(**user_dict)


# def fake_decode_token(token):
#     user = get_user(fake_users_db, token)
#     return user


# def fake_hash_password(password):
#     return('safe' + password)


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED,
#                             detail='Invalid authentication credentials',
#                             headers={'WWW-Authenticate': 'Bearer'})
#     return user


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if not current_user.is_active:
#         raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
#                             detail='Inactive user')
#     return current_user
# ###


router = APIRouter()

users = {}


@router.post('/player',  response_model=Player)
def create_new_player(player: PlayerBase):
    if not player.name:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail="That's a dumb name.")
    # test for duplicate name
    if player.name in [user.name for user in users.values()]:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
                            detail='Player name already taken.')

    player_id = ''.join(random.choice(string.ascii_uppercase)
                        for i in range(4))
    while player_id in users:
        # generate new game ids until a new id is found
        player_id = ''.join(random.choice(string.ascii_uppercase)
                            for i in range(4))

    users[player_id] = User(player.name, player_id)

    return users[player_id].to_json()


@router.get('/player', response_model=Player)
def get_player(player: PlayerBase):
    return users[player.uid]


# @router.post('/register_player', response_model=schemas.User)
# def register_player(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     print('try to create a player with name', user.name)
#     db_user = crud.get_user_by_name(db, user.name)
#     if db_user:
#         raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
#                             detail='User name is already taken.')
#     return crud.create_user(db=db, user=user)


# @router.post('/login_player', response_model=schemas.User)
# def login_player(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     pass


# @router.get('/tokens')
# async def read_tokens(token: str = Depends(oauth2_scheme)):
#     return {'token': token}


# def fake_decode_token(token):
#     return schemas.User(id=1, name=token+'fakedecoded')


# @router.get('/users/me')
# async def read_users_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# @router.post('/token')
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     # get(key) returns None if the key doesn't exist
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
#                             detail='Incorrect username or password')

#     user = schemas.UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=HTTP_400_BAD_REQUEST,
#                             detail='Incorrect username or password')

#     return {'access-token': user.name, 'token_type': 'bearer'}
