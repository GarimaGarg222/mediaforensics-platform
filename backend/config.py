from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "MediaForensics"
    app_env: str = "development"
    secret_key: str = "change-me"
    debug: bool = True

    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "mediaforensics"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # File storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 500
    allowed_extensions: str = "jpg,jpeg,png,webp,gif,mp4,mov,avi,mkv"

    # ML
    model_path: str = "./ml/weights/xception_best.pth"
    yolo_model: str = "yolov8n-face.pt"
    device: str = "cpu"

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"

    # Rate limiting
    rate_limit_uploads_per_minute: int = 10

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [e.strip() for e in self.allowed_extensions.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    model_config = {"env_file": ".env", "case_sensitive": False, "protected_namespaces": ()}


settings = Settings()
