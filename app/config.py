from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, List, Optional
import yaml
import os

class WeChatConfig(BaseSettings):
    """微信配置"""
    base_url: str = Field("http://127.0.0.1:8848/v849", description="WeChatPadPro API地址")
    auth_key: str = Field("", description="认证密钥")
    wxid: str = Field("", description="微信ID")
    
class MonitorConfig(BaseSettings):
    """监控配置"""
    bilibili_rooms: List[str] = Field(default_factory=list, description="B站直播间ID列表")
    weibo_users: List[str] = Field(default_factory=list, description="微博用户ID列表")
    douyin_users: List[str] = Field(default_factory=list, description="抖音用户ID列表")
    xiaohongshu_users: List[str] = Field(default_factory=list, description="小红书用户ID列表")
    
    check_interval: int = Field(60, description="检查间隔(秒)")
    max_retries: int = Field(3, description="最大重试次数")

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    url: str = Field("sqlite:///./wechat_monitor.db", description="数据库连接URL")

class RedisConfig(BaseSettings):
    """Redis配置"""
    host: str = Field("localhost", description="Redis主机")
    port: int = Field(6379, description="Redis端口")
    db: int = Field(0, description="Redis数据库")
    password: Optional[str] = Field(None, description="Redis密码")

class AppConfig(BaseSettings):
    """应用配置"""
    debug: bool = Field(False, description="调试模式")
    log_level: str = Field("INFO", description="日志级别")
    
    wechat: WeChatConfig = Field(default_factory=WeChatConfig)
    monitor: MonitorConfig = Field(default_factory=MonitorConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    
    # 目标群组配置
    target_groups: List[str] = Field(default_factory=list, description="目标微信群ID列表")
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

def load_config() -> AppConfig:
    """加载配置"""
    config_file = "config/config.yaml"
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            return AppConfig(**config_data)
    return AppConfig()

# ===== app/models.py =====
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class MonitorRecord(Base):
    """监控记录"""
    __tablename__ = "monitor_records"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # 平台名称
    user_id = Column(String(100), nullable=False)  # 用户ID
    content_id = Column(String(100), nullable=False)  # 内容ID
    content_type = Column(String(50), nullable=False)  # 内容类型
    title = Column(String(500))  # 标题
    content = Column(Text)  # 内容
    url = Column(String(500))  # 链接
    created_at = Column(DateTime, default=datetime.utcnow)
    is_sent = Column(Boolean, default=False)  # 是否已发送
    
class GroupConfig(Base):
    """群组配置"""
    __tablename__ = "group_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(String(100), nullable=False, unique=True)  # 群ID
    group_name = Column(String(200))  # 群名称
    is_active = Column(Boolean, default=True)  # 是否激活
    monitor_platforms = Column(String(500))  # 监控平台列表(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)