from .. import models, schemas, utils, oauth2
from typing import List
from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix= "/users",
    tags= ['Users']
)

# Create a user    
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user :schemas.CreateUser, db: Session = Depends(get_db)
                ):
                # , user_id: int= Depends(oauth2.get_current_user)):
    # hash the password 
    user.password = utils.get_password_hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# get a user
@router.get("/{id}",response_model=schemas.UserResponse)
def get_a_single_user(id, db: Session = Depends(get_db)
                      , user_id: int= Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.uuid == id).first()
    if user == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")

    return user

# get all users
@router.get("", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)
                  , user_id: int= Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users

#  update a user 
@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.UserResponse)
def update_user(id: str, user_update: schemas.UserBase, db: Session = Depends(get_db)
                , user_id: int= Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter(models.User.uuid == id)
    user = user_query.first()
    if user == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found")
    
    user_query.update(user_update.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()

# delete a user
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_usert(id: str, db: Session = Depends(get_db)
                 , user_id: int= Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.uuid == id)
    if user.first() == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"user with id {id} not found")
    user.delete(synchronize_session=False)
    db.commit()
    return 