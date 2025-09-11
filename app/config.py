from pydantic_settings import BaseSettings
from functools import lru_cache




class Settings(BaseSettings):
    database_url:str

    secret_key:str
    algorithm:str='HS256'
    access_token_expire_minutes:int=30


    google_client_id:str
    google_client_secret:str
    google_redirect_uri:str

    mail_username:str
    mail_password:str
    mail_from:str
    mail_port:int = 587
    mail_server:str='smtp.gmail.com'
    mail_from_name:str='Todo Habbit Tracker'

    redis_url:str

    app_name:str='Todo Habbit Tracker'
    debug:bool=False

    class Config:
        env_file='.env'


@lru_cache
def get_settings():
    return Settings()