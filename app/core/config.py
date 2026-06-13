from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # These attributes automatically map to the keys in your .env file
    DATABASE_URL: str
    REDIS_URL: str
    GEMINI_API_KEY: str = "" # Optional for now

    class Config:
        env_file = ".env"

# Create a global instance of settings to be imported across the app
settings = Settings()