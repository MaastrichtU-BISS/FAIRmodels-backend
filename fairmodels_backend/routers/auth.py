from datetime import time
from typing import Annotated, Dict, Union
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from data_layer import UserDataLayer, UserNotFoundException
import bcrypt
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')

router = APIRouter(prefix="/auth")

# https://testdriven.io/blog/fastapi-jwt-auth/
def token_response(token: str):
    return {
        "access_token": token
    }
def sign_jwt(username: str) -> Dict[str, str]:
    payload = {
        "username": username,
        "expires": time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decode_jwt(token: str) -> Union[dict, None]:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return None

def password_hash(password: str):
    # print("hashing ", bytes.decode(bcrypt.hashpw("haa".encode('utf-8'), bcrypt.gensalt())) )
    # return str(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))
    return bytes.decode(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()))

def password_check(password: str, hash: str):
    return bcrypt.checkpw(password.encode('utf-8'), hash)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    id: str
    username: str
    # email: Union[str, None] = None
    # full_name: Union[str, None] = None
    # disabled: Union[bool, None] = None

class UserInDB(User):
    password_hash: str


def get_user(username: str):
    try:
        user_layer = UserDataLayer()
        user = user_layer.find_by_username(username)
        return UserInDB(**user)
    except UserNotFoundException:
        return None

def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    username = decode_jwt(token)
    user = get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

class RegisterBody(BaseModel):
    username: str
    password: str

class LoginBody(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(req: RegisterBody):
    UserData = UserDataLayer()

    UserData.create(req.username, password_hash(req.password))

    return {"success": True}

@router.post("/token")
async def login(login_form: LoginBody):
    # user_layer = UserDataLayer()
    user = get_user(login_form.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserInDB(**user_dict)
    if not password_check(login_form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return sign_jwt(user.username)

@router.post("/generate_api_key")
async def generate_api_key(
    user: Annotated[User, Depends(get_current_user)]
):
    user_layer = UserDataLayer()
    user_layer.generate_api_key(user.id)

@router.get("/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

# Legacy:
# @app.get("/auth_link")
# def cli_auth():
#   api = orcid.PublicAPI(os.getenv("ORCID_CLIENT_ID"), os.getenv("ORCID_CLIENT_SECRET"), sandbox=False)
#   url = api.get_login_url(scope="/authenticate", redirect_uri="http://0.0.0.0:3099/redirect")
#   return {"url": url}