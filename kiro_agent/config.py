"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str = "mock-key"
    aws_secret_access_key: str = "mock-secret"

    # App
    environment: str = "dev"
    server_port: int = 8080
    log_level: str = "INFO"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://kiro-dashboard.amplifyapp.com",
    ]

    # CloudWatch
    cloudwatch_log_group_prefix: str = "/ecs/kiro-"

    # DynamoDB Tables
    dynamodb_knowledge_table: str = "KnowledgeTable"
    dynamodb_tickets_table: str = "TicketsTable"
    dynamodb_incidents_table: str = "IncidentsTable"

    # Agent (kiro-agent repo endpoint for diagnose forwarding)
    agent_endpoint: str = "http://localhost:8081"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
