from multiprocessing import synchronize
from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import security
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy.orm import Session, load_only
from sqlalchemy import orm
import datetime
import uvicorn
import os
import jwt

import schemas
import models
from database import Base, engine, SessionLocal
import utils

oauth2schema = security.OAuth2PasswordBearer('/user/token')

Base.metadata.create_all(engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
    except:
        print('error')
    finally:
        session.close()

app = FastAPI()
router = InferringRouter()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post('/user/register')
async def create_user(user:schemas.UserCreate, session:Session=Depends(get_session)):
    user = await utils.create_user(user=user, db=session)
    return await utils.create_token(user=user)

@app.post('/user/token')
async def generate_token(form_data: security.OAuth2PasswordRequestForm = Depends(), session:Session=Depends(get_session)):
    user = await utils.authenticate_user(email=form_data.username, password=form_data.password, session=session)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    return await utils.create_token(user=user)


def get_current_user(session:orm.Session=Depends(get_session), token: str=Depends(oauth2schema)):
    try:
        payload = jwt.decode(token,utils.jwt_secret, algorithms=['HS256'])
        user = session.query(models.User).get(payload['id'])
    except:
        raise HTTPException(status_code=401, detail='Invalid Credentials')
    return schemas.User.from_orm(user)

@app.post('/user/me',response_model=schemas.User)
async def get_user(user:schemas.User= Depends(get_current_user)):
    return user

@cbv(router)  # Step 2: Create and decorate a class to hold the endpoints
class CompanyCBV:
    # Step 3: Add dependencies as class attributes
    session: Session = Depends(get_session)
    model_used = models.Company
    url = '/companies'
    url_id = url+'/:id'

    @router.get(url)
    def get_items(self):
        items = self.session.query(self.model_used).all()
        return items
    
    @router.post(url)
    def create_item(self, item: schemas.Company, user:schemas.User=Depends(get_current_user)):
        item = self.model_used(**item.dict())
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    @router.get(url_id)
    def get_item(self, id:int):
        item = self.session.query(self.model_used).get(id)
        return item

    @router.put(url_id)
    def update_item(self, id:int, body: schemas.Company, user:schemas.User=Depends(get_current_user)):
        item = self.session.query(self.model_used).filter(self.model_used.id==id).first()
        item.update(**body.dict(exclude_unset=True))
        self.session.commit()
        return item

    @router.delete(url_id)
    def item_delete(self, id:int, user:schemas.User=Depends(get_current_user)):
        item = self.session.query(self.model_used).get(id)
        self.session.delete(item)
        self.session.commit()
        return {}


@cbv(router)  # Step 2: Create and decorate a class to hold the endpoints
class ProductCBV:
    # Step 3: Add dependencies as class attributes
    session: Session = Depends(get_session)
    model_used = models.Product
    url = '/products'
    url_id = url+'/:id'

    @router.get(url)
    def get_items(self):
        items = self.session.query(self.model_used).all()
        return items
    
    @router.post(url)
    async def create_item(self, item: schemas.Product, user:schemas.User=Depends(get_current_user)):
        foreign = await utils.check_foreign_key(self.session, models.Company, models.Company.id, item.company_id)
        if foreign:
            item = self.model_used(**item.dict())
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
            return item
        else:
            raise HTTPException(status_code=400, detail='company with that id does not exist')

    @router.get(url_id)
    def get_item(self, id:int):
        item = self.session.query(self.model_used).get(id)
        return item

    @router.put(url_id)
    def update_item(self, id:int, body: schemas.ProductUpdate, user:schemas.User=Depends(get_current_user)):
        item = self.session.query(self.model_used).filter(self.model_used.id==id).first()
        item.update(**body.dict(exclude_unset=True))
        self.session.commit()
        return item

    @router.delete(url_id)
    def item_delete(self, id:int, user:schemas.User=Depends(get_current_user)):
        item = self.session.query(self.model_used).get(id)
        self.session.delete(item)
        self.session.commit()
        return {}


@cbv(router)  # Step 2: Create and decorate a class to hold the endpoints
class ProductCheckCBV:
    # Step 3: Add dependencies as class attributes
    session: Session = Depends(get_session)
    model_used = models.ProductCheck
    url = '/products/check'
    url_id = url+'/:id'

    @router.get(url)
    def get_items(self):
        items = self.session.query(self.model_used).all()
        return items
    
    @router.post(url)
    async def create_item(self, item: schemas.ProductCheck, user:schemas.User=Depends(get_current_user)):
        foreign = await utils.check_foreign_key(self.session, models.Product, models.Product.id, item.product_id)
        if foreign:
            item = self.model_used(**item.dict())
            self.session.add(item)
            self.session.commit()
            self.session.refresh(item)
            return item
        else:
            raise HTTPException(status_code=400, detail='product with that id does not exist')

    @router.get(url_id)
    def get_item(self, id:int):
        item = self.session.query(self.model_used).get(id)
        return item

    @router.put(url_id)
    def update_item(self, id:int, body: schemas.ProductCheckUpdate, user:schemas.User=Depends(get_current_user)):
        item = self.session.query(self.model_used).filter(self.model_used.id==id).first()
        item.update(**body.dict(exclude_unset=True))
        self.session.commit()
        return item

    @router.delete(url_id)
    def item_delete(self, id:int, user:schemas.User=Depends(get_current_user)):
        item = self.session.query(self.model_used).get(id)
        self.session.delete(item)
        self.session.commit()
        return {}
        
    


app.include_router(router)


# app.mount("/images", StaticFiles(directory='images'), 'images')
# app.mount('/', StaticFiles(directory='client',html=True), name='templates')

if __name__=='__main__':
    port = os.getenv('PORT',default=8000)
    app_str = 'app:app'
    uvicorn.run(app_str, host='0.0.0.0', port=int(port) or 8000, reload=True)