from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_pwd: str
    db_name: str

    es_host: str
    es_port: int

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pwd}@{self.db_host}:{self.db_port}/{self.db_name}?async_fallback=True"
    
    @property
    def es_url(self) -> str:
        return f"http://{self.es_host}:{self.es_port}/"


settings = Settings(
    _env_file=".env",
    _env_file_encoding="utf-8",
)