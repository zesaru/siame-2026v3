#!/usr/bin/env python3
"""
Security Guardian Agent - Main Entry Point
Agente especializado en seguridad, auditoría y cumplimiento ENS Alto
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
    title="Security Guardian Agent",
    description="Agente especializado en seguridad y auditoría ENS Alto",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "agent": "security_guardian",
        "status": "running",
        "version": "1.0.0",
        "security_level": os.getenv("SECURITY_LEVEL", "ENS_ALTO")
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent_type": "security_guardian"
    }


async def main():
    """Main entry point"""
    port = int(os.getenv("AGENT_PORT", "8004"))
    host = os.getenv("AGENT_HOST", "0.0.0.0")

    print(f"🚀 Starting Security Guardian Agent on {host}:{port}")
    print(f"🔒 Security Level: {os.getenv('SECURITY_LEVEL', 'ENS_ALTO')}")

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
