from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import crud, models, schemas, config
from .database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)
api_key_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_service_user(api_key: str = Depends(api_key_header_scheme), db: Session = Depends(get_db)):
    if api_key == config.settings.ADMIN_API_KEY:
        admin_user = crud.get_user_by_email(db, email="admin@gtvision.com")
        if admin_user:
            return admin_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key for service")