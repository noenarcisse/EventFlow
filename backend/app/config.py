from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://eventflow:eventflow@db:5432/eventflow"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 120
    reservation_minutes: int = 10
    # Feature flag for the pedagogical fil rouge. When True, intentional bugs
    # (B1..B12) are activated module by module. Kept False in the skeleton.
    seed_bugs: bool = False
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
