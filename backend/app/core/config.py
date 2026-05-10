from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Central application settings.
    Reads values from backend/.env and provides strongly typed access
    across the application.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="FitFuel AI API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://fitfuel:fitfuel_dev_password@localhost:5432/fitfuel",
        alias="DATABASE_URL",
    )

    # JWT
    jwt_secret_key: str = Field(default="change-this-secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ORIGINS",
    )

    # Cloudinary
    cloudinary_cloud_name: str = Field(default="", alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str = Field(default="", alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str = Field(default="", alias="CLOUDINARY_API_SECRET")

    # Uploads
    local_upload_dir: str = Field(
        default=str(BASE_DIR / "uploads"),
        alias="LOCAL_UPLOAD_DIR",
    )
    max_photo_upload_mb: int = Field(default=10, alias="MAX_PHOTO_UPLOAD_MB")

    # Vision
    vision_device: str = Field(default="auto", alias="VISION_DEVICE")
    vision_model_path: str = Field(default="", alias="VISION_MODEL_PATH")
    vision_class_names_path: str = Field(default="", alias="VISION_CLASS_NAMES_PATH")
    vision_binary_model_path: str = Field(
        default=str(BASE_DIR / "ml_artifacts" / "binary_resnet50_best.pth"),
        alias="VISION_BINARY_MODEL_PATH",
    )
    vision_binary_class_names_path: str = Field(
        default=str(BASE_DIR / "ml_artifacts" / "binary_class_names.json"),
        alias="VISION_BINARY_CLASS_NAMES_PATH",
    )
    vision_food_model_path: str = Field(
        default=str(BASE_DIR / "ml_artifacts" / "food101_subset_resnet50_best.pth"),
        alias="VISION_FOOD_MODEL_PATH",
    )
    vision_food_class_names_path: str = Field(
        default=str(BASE_DIR / "ml_artifacts" / "food101_subset_class_names.json"),
        alias="VISION_FOOD_CLASS_NAMES_PATH",
    )
    vision_food_accept_threshold: float = Field(default=0.90, alias="VISION_FOOD_ACCEPT_THRESHOLD")
    vision_class_accept_threshold: float = Field(default=0.75, alias="VISION_CLASS_ACCEPT_THRESHOLD")
    vision_top_k: int = Field(default=5, alias="VISION_TOP_K")
    vision_default_serving_grams: float = Field(default=100.0, alias="VISION_DEFAULT_SERVING_GRAMS")

    # Gemini chat assistant
    gemini_enabled: bool = Field(default=False, alias="GEMINI_ENABLED")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_MODEL")
    gemini_temperature: float = Field(default=0.2, alias="GEMINI_TEMPERATURE")
    gemini_max_output_tokens: int = Field(default=1024, alias="GEMINI_MAX_OUTPUT_TOKENS")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def gemini_is_configured(self) -> bool:
        return self.gemini_enabled and bool(self.gemini_api_key.strip())


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
