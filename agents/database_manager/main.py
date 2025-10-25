#!/usr/bin/env python3
"""
Database Manager Agent - Main Entry Point
Agente especializado en gestión de PostgreSQL y migraciones
"""
import asyncio
import os
import sys
from pathlib import Path

# Agregar rutas al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI
from uvicorn import Config, Server

app = FastAPI(
    title="Database Manager Agent",
    description="Agente especializado en gestión de base de datos PostgreSQL",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "agent": "database_manager",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent_type": "database_manager"
    }


async def main():
    """Main entry point"""
    port = int(os.getenv("AGENT_PORT", "8002"))
    host = os.getenv("AGENT_HOST", "0.0.0.0")

    print(f"🚀 Starting Database Manager Agent on {host}:{port}")

    config = Config(
        app=app,
        host=host,
        port=port,
        log_level="info"
    )

    server = Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
