#!/usr/bin/env python3
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_organization: Optional[str] = None

    # LangSmith
    langsmith_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None

    # Azure
    azure_service_bus_conn: Optional[str] = None
    azure_service_bus_topic: Optional[str] = None
    azure_service_bus_sub: Optional[str] = None
    azure_cosmos_conn: Optional[str] = None
    azure_cosmos_db: Optional[str] = None
    azure_cosmos_container: Optional[str] = None

    # App
    environment: str = os.getenv("APP_ENV", "dev")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Redis
    redis_url: Optional[str] = None


def load_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        openai_organization=os.getenv("OPENAI_ORG"),
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        langsmith_project=os.getenv("LANGSMITH_PROJECT", "rm-mvp"),
        azure_service_bus_conn=os.getenv("AZURE_SERVICE_BUS_CONNECTION"),
        azure_service_bus_topic=os.getenv("AZURE_SERVICE_BUS_TOPIC", "rm-events"),
        azure_service_bus_sub=os.getenv("AZURE_SERVICE_BUS_SUB", "reasoner-workers"),
        azure_cosmos_conn=os.getenv("AZURE_COSMOS_CONNECTION"),
        azure_cosmos_db=os.getenv("AZURE_COSMOS_DB", "rm_mvp"),
        azure_cosmos_container=os.getenv("AZURE_COSMOS_CONTAINER", "sessions"),
        environment=os.getenv("APP_ENV", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        redis_url=os.getenv("REDIS_URL"),
    )
