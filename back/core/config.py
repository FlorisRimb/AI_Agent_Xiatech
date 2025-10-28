from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Retail Inventory"
    MONGO_URL: str

    class Config:
        env_file = ".env"


settings = Settings()