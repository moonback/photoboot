from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = Field(8000, ge=1, le=65535)
    workers: int = Field(1, ge=1, le=10)


class SecurityConfig(BaseModel):
    secret_key: str
    session_timeout: int = Field(3600, ge=300, le=86400)  # 5min à 24h
    bcrypt_rounds: int = Field(12, ge=10, le=16)


class AdminConfig(BaseModel):
    username: str
    password_hash: str


class StorageConfig(BaseModel):
    upload_dir: str = "uploads"
    max_file_size: int = Field(10485760, ge=1024, le=104857600)  # 1KB à 100MB
    allowed_extensions: List[str] = [".jpg", ".jpeg", ".png", ".gif"]


class LoggingConfig(BaseModel):
    level: LogLevel = LogLevel.INFO
    rotation: str = "1 day"
    retention: str = "30 days"
    format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"


class CameraConfig(BaseModel):
    device_id: int = Field(0, ge=0)
    resolution: List[int] = [1920, 1080]
    fps: int = Field(30, ge=1, le=60)


class UIConfig(BaseModel):
    fullscreen: bool = True
    theme: str = "dark"
    language: str = "fr"


class AppConfig(BaseModel):
    name: str = "Photobooth"
    version: str = "1.0.0"
    debug: bool = False


class Config(BaseModel):
    app: AppConfig
    server: ServerConfig
    security: SecurityConfig
    admin: AdminConfig
    storage: StorageConfig
    logging: LoggingConfig
    camera: CameraConfig
    ui: UIConfig


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str
    uptime: float


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None


class LogoutResponse(BaseModel):
    success: bool
    message: str


class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any]


class ConfigResponse(BaseModel):
    config: Config
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# Modèles pour les cadres
class FrameCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field("", max_length=500)
    position: str = Field("center", pattern="^(center|top-left|top-right|bottom-left|bottom-right|custom)$")
    size: int = Field(100, ge=10, le=200)
    active: bool = False
    x: Optional[int] = Field(None, ge=0, le=100)
    y: Optional[int] = Field(None, ge=0, le=100)


class FrameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    position: Optional[str] = Field(None, pattern="^(center|top-left|top-right|bottom-left|bottom-right|custom)$")
    size: Optional[int] = Field(None, ge=10, le=200)
    active: Optional[bool] = None
    x: Optional[int] = Field(None, ge=0, le=100)
    y: Optional[int] = Field(None, ge=0, le=100)


class Frame(BaseModel):
    id: str
    name: str
    description: Optional[str]
    filename: str
    position: str
    size: int
    active: bool
    width: int
    height: int
    created_at: str
    created_by: str
    x: Optional[int] = None
    y: Optional[int] = None


class FrameResponse(BaseModel):
    frame: Frame


class FramesResponse(BaseModel):
    frames: List[Frame]
