from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./eventos_academicos.db"
    app_name: str = "API de Gestão de Eventos Acadêmicos"
    api_prefix: str = "/api/v1"

    # Defina JWT_SECRET_KEY no arquivo .env. Use uma chave aleatória com pelo menos 32 caracteres.
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=30, gt=0)

    # Credenciais usadas somente pelo provisionamento do primeiro administrador.
    admin_name: str = "Administrador"
    admin_email: str | None = None
    admin_password: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
