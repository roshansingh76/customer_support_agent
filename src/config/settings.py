from pydantic_settings import SettingsConfigDict,BaseSettings
from pydantic import SecretStr, Field
from sqlalchemy import URL

class Settings(BaseSettings):


        DB_USER:str
        DB_PASSWORD:str
        DB_HOST:str
        DB_PORT:int=5432
        DB_NAME:str

        DB_POOL_SIZE: int = Field(default=10, ge=1)
        DB_MAX_OVERFLOW: int = Field(default=20, ge=0)
        DB_POOL_TIMEOUT: int = Field(default=30, gt=0)
        DB_POOL_RECYCLE: int = Field(default=1800, gt=0)
        DB_ECHO: bool = False


        APP_NAME: str = "My Application"
        DEBUG: bool = False

        JWT_SECRET_KEY: str
        JWT_ALGORITHM: str = "HS256"

        ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
        REFRESH_TOKEN_EXPIRE_DAYS: int = 7


        @property
        def DATABASE_URL(self) -> str:
            return URL.create(
                drivername="postgresql+psycopg",
                username=self.DB_USER,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.DB_NAME,
         )
        model_config=SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore"
            
        )




settings =Settings()