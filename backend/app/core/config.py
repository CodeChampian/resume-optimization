from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "resume_optimizer"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-pro-exp-03-25"
    storage_path: str = "storage"
    cors_origins: str = "http://localhost:5173"

    @property
    def templates_dir(self) -> str:
        return f"{self.storage_path}/templates"

    @property
    def generated_dir(self) -> str:
        return f"{self.storage_path}/generated"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
