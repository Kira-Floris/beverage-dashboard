from itertools import product
from unicodedata import category
from pydantic import BaseModel
import datetime
from typing import Optional
from typing_extensions import Literal
import datetime
import models

class UserBase(BaseModel):
    email:str

class UserCreate(UserBase):
    password:str

    class Config:
        orm_mode=True

class User(UserBase):
    id:int
    date_created:datetime.datetime

    class Config:
        orm_mode=True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    company_id: int

class Company(BaseModel):
    title: str
    category: Optional[str] = None
    address: Optional[str] = None

class ProductUpdate(BaseModel):
    title:Optional[str]=None
    description:Optional[str]=None

class ProductCheck(BaseModel):
    category: Literal['sugar','alcohol','water']
    date: datetime.date
    product_id: int

class ProductCheckUpdate(BaseModel):
    category:Optional[Literal['sugar','alcohol','water']]=None

