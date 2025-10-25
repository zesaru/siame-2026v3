#!/usr/bin/env python3
"""
Document Processor Agent - Main Entry Point
Agente especializado en procesamiento y OCR de documentos diplomáticos
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
    title="Document Processor Agent",
    description="Agente especializado en procesamiento de documentos con Azure Form Recognizer",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "agent": "document_processor",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "agent_type": "document_processor"
    }


@app.post("/process")
async def process_document(document_path: str):
    """
    Procesar un documento diplomático
    """
    # TODO: Implementar usando azure_form_recognizer_agent.py
    return {
        "status": "processing",
        "document": document_path
    }


async def main():
    """Main entry point"""
    port = int(os.getenv("AGENT_PORT", "8001"))
    host = os.getenv("AGENT_HOST", "0.0.0.0")

    print(f"🚀 Starting Document Processor Agent on {host}:{port}")

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
