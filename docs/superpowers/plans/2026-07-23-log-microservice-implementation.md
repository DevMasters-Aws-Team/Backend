# E-Commerce Production Log Generator Microservice Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a clean, high-performance FastAPI microservice and traffic simulator that streams structured JSON logs (containing request/response payloads and fictitious user identity data like DNI, names, emails, IPs) to AWS CloudWatch and stdout.

**Tech Stack:** Python 3.12, FastAPI 0.110+, Poetry (`pyproject.toml`), `uv`, `boto3`, `pydantic` v2, `structlog`, `pytest` + `moto`, `Dockerfile`, `docker-compose.yml`, `Makefile`.
