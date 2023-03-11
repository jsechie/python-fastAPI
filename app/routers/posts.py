from sqlalchemy import func
from .. import models, oauth2, schemas
from typing import List, Optional
from fastapi import Depends, APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags= ['Posts']
)

# get all post
@router.get("/", response_model=List[schemas.PostVote])
def get_all_posts(db: Session = Depends(get_db),
                  search: Optional[str] = "", 
                  limit: int = 10,
                  skip: int = 0 ):
# def get_all_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # posts = db.query(models.Post).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    posts = results.filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

# post a post to db
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostVote)
def create_post(post :schemas.CreatePost, db: Session = Depends(get_db)
                , current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    results = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    post = results.filter(models.Post.id == new_post.id).first()
    return post

# get a post
@router.get("/{id}",response_model=schemas.PostVote)
def get_a_single_post(id, db: Session = Depends(get_db)):
    # post = db.query(models.Post).filter(models.Post.uuid == id).first()
    results = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    post = results.filter(models.Post.uuid == id).first()
    if post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")

    return post

# delete a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: str, db: Session = Depends(get_db)
                , current_user: int= Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.uuid == id)
    user_post = post.first()
    if user_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if user_post.user_id != int(current_user.id):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail=f"You are not ALLOWED to perform this action")
    post.delete(synchronize_session=False)
    db.commit()
    return 

#  update a post 
@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostVote)
def update_post(id: str, post_update: schemas.UpdatePost, db: Session = Depends(get_db)
                , current_user: int= Depends(oauth2.get_current_user)):
    results = db.query(models.Post, func.count(models.Vote.post_id).label("likes")).join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id)
    post_query = db.query(models.Post).filter(models.Post.uuid == id)
    user_post = post_query.first()
    if user_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if user_post.user_id != int(current_user.id):
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail=f"You are not ALLOWED to perform this action")
    post_query.update(post_update.dict(), synchronize_session=False)
    db.commit()
    user_post = results.filter(models.Post.uuid == id).first()
    return user_post
