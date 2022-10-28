from secrets import token_bytes
from sqlalchemy import orm
from passlib import hash
import jwt
from fastapi import Depends, security, HTTPException

import models
import schemas

jwt_secret = 'jaskdjaiu132nj23hj'

async def get_user_by_email(email:str, db: orm.Session):
    return db.query(models.User).filter(models.User.email==email).first()

async def create_user(user:schemas.UserCreate, db:orm.Session):
    hashed_password = hash.bcrypt.hash(user.password)
    user_obj = models.User(email=user.email, hashed_password=hashed_password)

    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def create_token(user:models.User):
    user_schema_obj = schemas.User.from_orm(user)
    user_dict = user_schema_obj.dict()
    del user_dict['date_created']
    token = jwt.encode(user_dict, jwt_secret)
    return dict(access_token=token, token_type='bearer')

async def authenticate_user(email:str, password:str, session:orm.Session):
    user = await get_user_by_email(email=email, db=session)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user

async def check_foreign_key(session:orm.Session, parent_model, foreign_variable, foreign_value):
    item = session.query(parent_model).filter(foreign_variable==foreign_value).first()
    if item:
        return True
    return False