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


class PrintingConfig(BaseModel):
    default_printer: str = ""
    paper_size: str = Field("4x6", pattern="^(4x6|5x7|6x8|A4|letter)$")
    quality: str = Field("normal", pattern="^(draft|normal|high|photo)$")
    max_copies: int = Field(5, ge=1, le=10)
    retry_attempts: int = Field(3, ge=1, le=5)
    retry_delay: int = Field(2, ge=1, le=10)


class EmailConfig(BaseModel):
    smtp_server: str = ""
    smtp_port: int = Field(587, ge=1, le=65535)
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    from_name: str = "Photobooth"
    subject_template: str = "Votre photo Photobooth"
    body_template: str = ""
    max_attachment_size: int = Field(10485760, ge=1048576, le=52428800)  # 1MB à 50MB
    thumbnail_size: List[int] = [300, 300]
    thumbnail_quality: int = Field(85, ge=50, le=100)
    gdpr_consent_required: bool = True
    gdpr_consent_text: str = ""
    gdpr_retention_days: int = Field(30, ge=1, le=365)
    rate_limit_emails: int = Field(10, ge=1, le=100)
    rate_limit_window: int = Field(3600, ge=300, le=86400)  # 5min à 24h


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
    printing: PrintingConfig
    email: EmailConfig


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    version: str
    uptime: float
    camera_status: Dict[str, Any]
    disk_space: Dict[str, Any]
    printer_status: Dict[str, Any]
    email_status: Dict[str, Any]


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


# Modèles pour l'impression
class PrintRequest(BaseModel):
    photo_path: str
    copies: int = Field(1, ge=1, le=10)
    printer_name: Optional[str] = None


class PrintResponse(BaseModel):
    success: bool
    message: str
    printer: Optional[str] = None
    copies: Optional[int] = None
    method: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None


class PrinterInfo(BaseModel):
    name: str
    port: str
    description: str
    platform: str


class PrintersResponse(BaseModel):
    printers: List[PrinterInfo]
    default_printer: Optional[str] = None


# Modèles pour l'email
class EmailRequest(BaseModel):
    to_email: str
    photo_path: str
    download_link: str
    consent_given: bool = False
    user_name: str = ""


class EmailResponse(BaseModel):
    success: bool
    message: str
    to: Optional[str] = None
    timestamp: Optional[float] = None
    error: Optional[str] = None
    details: Optional[str] = None


class GdprConsentResponse(BaseModel):
    consent_text: str
    required: bool
    retention_days: int


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
