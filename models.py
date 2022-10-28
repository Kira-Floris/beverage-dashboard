from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils.types.choice import ChoiceType

import datetime
from passlib import hash

from database import Base

class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    hashed_password = Column(String)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)

    def verify_password(self, password:str):
        return hash.bcrypt.verify(password, self.hashed_password)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Company(Base):
    __tablename__ = 'Company'

    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    category = Column(String(256))
    address = Column(String(256))

    product = relationship('Product', back_populates='company')

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            

class Product(Base):
    __tablename__ = 'Product'

    id = Column(Integer, primary_key=True)
    title = Column(String(256), unique=True)
    description = Column(String(256))
    company_id = Column(Integer, ForeignKey('Company.id'))

    company = relationship('Company',back_populates='product')
    productcheck = relationship('ProductCheck', back_populates='product')

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

categories_check = [
        ('sugar','sugar'),
        ('alcohol','alcohol'),
        ('water','water')
    ]
categories_check_list = ['sugar','alcohol','water']

class ProductCheck(Base):
    __tablename__ = 'ProductCheck'

    id = Column(Integer, primary_key=True)
    category = Column(ChoiceType(categories_check))
    date = Column(Date)
    product_id = Column(Integer, ForeignKey('Product.id'))

    product = relationship('Product', back_populates='productcheck')

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)