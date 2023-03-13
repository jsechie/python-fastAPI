from typing import List, Optional
from pydantic import BaseModel, EmailStr, conint

# User login 
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Post class base model 
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

# Post creation validation 
class CreatePost(PostBase):
    pass

# Update user body validation     
class UpdatePost(PostBase):
    published: bool

# User model base class 
class UserBase(BaseModel):
    username: str

# Validate user crestion body
class CreateUser(UserBase):
    password: str
    firstname: str
    lastname: str
    email: EmailStr

# Validate user crestion body
class UpdateUser(UserBase):
    firstname: str
    lastname: str
    email: EmailStr

# User response formatter
class UserResponse(UserBase):
    firstname: str
    lastname: str
    email: EmailStr
    uuid: str
    id: int
    class Config:
        orm_mode = True


class PostUser(UserBase):
    class Config:
        orm_mode = True

# Post model response class 
class PostResponse(PostBase):
    id: int
    uuid: str
    posted_by: PostUser 
    class Config:
        orm_mode = True

# post with votes 
class PostVote(BaseModel):
    Post: PostResponse
    likes: int
    class Config:
        orm_mode = True

# Token model 
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: str

# token data 
class TokenData(BaseModel):
    id : str
    # id : Optional[str] = None

# voting
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)