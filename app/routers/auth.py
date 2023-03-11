from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags= ["Authentication"]
)


@router.post("/login",response_model=schemas.Token)
def login(user_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_cred.username).first()
    if user == None:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Email or Password Incorrect")
    if not utils.verify_password(user_cred.password, user.password):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="Email or Password Incorrect")

    # create a token
    access_token = oauth2.create_access_token(data={'id':user.id})
    # return token
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": f"{oauth2.ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
    }
