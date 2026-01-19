from typing import List, Union

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    API_V1_STR: str
    DEBUG: bool
    ALLOWED_HOSTS: Union[List[str], str]
    CORS_ORIGINS: Union[List[str], str]
    LOG_LEVEL: str
    TIMEZONE: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    # Timeouts (in seconds)
    HTTP_CLIENT_TIMEOUT: int
    DATABASE_TIMEOUT: int
    EXTERNAL_SERVICE_TIMEOUT: int
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool
    RATE_LIMIT_PER_MINUTE: int
    RATE_LIMIT_BURST: int
    
    # Idempotency
    IDEMPOTENCY_ENABLED: bool
    IDEMPOTENCY_TTL_SECONDS: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @field_validator("ALLOWED_HOSTS", "CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_list_from_str(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


settings = Settings()
