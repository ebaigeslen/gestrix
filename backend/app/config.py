from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "gestrix-seo"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"
    DATABASE_URL: str = "sqlite:///./data/gestrix.db"
    DATA_DIR: str = "./data"
