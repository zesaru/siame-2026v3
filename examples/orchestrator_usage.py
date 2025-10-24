#!/usr/bin/env python3
"""
SIAME 2026v3 - Ejemplo de uso del Orchestrator
Demuestra cómo usar el orchestrator para procesar comandos y documentos diplomáticos

Este ejemplo muestra:
- Inicialización del orchestrator
- Procesamiento de comandos en lenguaje natural
- Creación de sistemas completos
- Procesamiento de documentos diplomáticos
- Monitoreo del estado del sistema
"""

import asyncio
import logging
from pathlib import Path
import sys

# Agregar path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from orchestrator.siame_orchestrator import SiameOrchestrator, SecurityLevel, DiplomaticDocumentType
from agents.azure_form_recognizer_agent import FormRecognizerConfig


async def demo_orchestrator_usage():
    """Demostración completa del uso del orchestrator SIAME"""

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("=" * 60)
    print("SIAME 2026v3 - Demostración del Orchestrator")
    print("Sistema Inteligente de Análisis Multiagente Especializado")
    print("=" * 60)

    # Inicializar orchestrator
    orchestrator = SiameOrchestrator()

    try:
        print("\n1. Inicializando SIAME Orchestrator...")
        success = await orchestrator.initialize()

        if not success:
            print("❌ Error inicializando orchestrator")
            return

        print("✅ Orchestrator inicializado exitosamente")

        # Mostrar estado inicial
        status = await orchestrator.get_system_status()
        print(f"\n📊 Estado del sistema:")
        print(f"   - Agentes especializados: {status['specialized_agents']['total']}")
        print(f"   - Comandos activos: {status['active_commands']}")
        print(f"   - Documentos procesados: {status['diplomatic_documents']}")
        print(f"   - Azure Form Recognizer: {'✅' if status['azure_services']['form_recognizer_configured'] else '❌'}")

        print(f"\n🎯 Comandos disponibles:")
        for i, cmd in enumerate(status['available_commands'], 1):
            print(f"   {i}. {cmd}")

        # Demostrar comandos
        await demo_commands(orchestrator)

        # Demostrar procesamiento de documentos
        await demo_document_processing(orchestrator)

        # Demostrar creación de sistema completo
        await demo_system_creation(orchestrator)

        # Mostrar estadísticas finales
        await show_final_statistics(orchestrator)

    except Exception as e:
        print(f"❌ Error en demostración: {e}")
        logging.exception("Error en demostración")

    finally:
        print("\n🔄 Cerrando orchestrator...")
        await orchestrator.shutdown()
        print("✅ Demostración completada")


async def demo_commands(orchestrator):
    """Demuestra el procesamiento de comandos"""
    print("\n" + "=" * 40)
    print("2. DEMOSTRACIÓN DE COMANDOS")
    print("=" * 40)

    commands_to_test = [
        "Crear sistema completo SIAME",
        "Implementar autenticación con niveles",
        "Configurar Azure Form Recognizer",
        "Generar base de datos con Prisma",
        "Desplegar sistema en staging"
    ]

    for i, command in enumerate(commands_to_test, 1):
        print(f"\n📝 Comando {i}: {command}")

        try:
            result = await orchestrator.process_command(
                command,
                SecurityLevel.RESTRICTED,
                {"environment": "development", "azure_region": "East US"}
            )
            print(f"   ✅ Resultado: {result}")

            # Simular espera de procesamiento
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"   ❌ Error: {e}")


async def demo_document_processing(orchestrator):
    """Demuestra el procesamiento de documentos diplomáticos"""
    print("\n" + "=" * 40)
    print("3. PROCESAMIENTO DE DOCUMENTOS")
    print("=" * 40)

    # Crear documentos de ejemplo para demostración
    demo_documents = [
        {
            "name": "hoja_remision_001.txt",
            "type": DiplomaticDocumentType.HOJA_REMISION,
            "content": """
HOJA DE REMISIÓN HR-2024-001

Fecha: 15 de enero de 2024
Origen: Cancillería Nacional
Destino: Embajada en Francia
Clasificación: CONFIDENCIAL

Número de Remisión: HR-2024-001
Tipo de Documento: Correspondencia Oficial
Descripción: Instrucciones para negociación comercial
Responsable: Embajador Juan Pérez
            """.strip()
        },
        {
            "name": "guia_valija_002.txt",
            "type": DiplomaticDocumentType.GUIA_VALIJA,
            "content": """
GUÍA DE VALIJA DIPLOMÁTICA GV-2024-045

Fecha de Envío: 16 de enero de 2024
Valija Número: VAL-789
Peso Total: 2.5 kg
Cantidad de Documentos: 15
Destino: Consulado en Madrid
Transportista: DHL Express
Observaciones: Entrega urgente - documentos clasificados
            """.strip()
        }
    ]

    # Crear directorio temporal para documentos
    temp_dir = Path("temp_documents")
    temp_dir.mkdir(exist_ok=True)

    try:
        for doc_info in demo_documents:
            print(f"\n📄 Procesando: {doc_info['name']}")

            # Crear archivo temporal
            doc_path = temp_dir / doc_info['name']
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(doc_info['content'])

            try:
                # Procesar documento
                workflow_id = await orchestrator.process_diplomatic_document(
                    doc_path,
                    doc_info['type'],
                    SecurityLevel.CONFIDENTIAL
                )

                print(f"   ✅ Workflow iniciado: {workflow_id}")

                # Verificar estado del workflow
                await asyncio.sleep(1)  # Simular procesamiento

                workflow_status = await orchestrator.get_workflow_status(workflow_id)
                print(f"   📊 Estado del workflow: {workflow_status.get('overall_progress', 0):.0%} completado")

            except Exception as e:
                print(f"   ❌ Error procesando documento: {e}")

    finally:
        # Limpiar archivos temporales
        try:
            for doc_info in demo_documents:
                doc_path = temp_dir / doc_info['name']
                if doc_path.exists():
                    doc_path.unlink()
            temp_dir.rmdir()
        except:
            pass


async def demo_system_creation(orchestrator):
    """Demuestra la creación de un sistema completo"""
    print("\n" + "=" * 40)
    print("4. CREACIÓN DE SISTEMA COMPLETO")
    print("=" * 40)

    print("\n🏗️  Creando sistema SIAME completo...")

    features = [
        "nextjs_frontend",
        "azure_integration",
        "postgresql_database",
        "authentication_system",
        "form_recognizer",
        "diplomatic_processing",
        "security_classification",
        "api_rest",
        "real_time_updates"
    ]

    try:
        workflow_id = await orchestrator.create_complete_siame_system(
            project_name="siame-demo-2026v3",
            features=features
        )

        print(f"✅ Sistema creado exitosamente")
        print(f"   📋 Workflow ID: {workflow_id}")
        print(f"   🎯 Características incluidas:")

        for feature in features:
            print(f"      • {feature.replace('_', ' ').title()}")

        # Verificar progreso
        await asyncio.sleep(2)  # Simular tiempo de creación

        workflow_status = await orchestrator.get_workflow_status(workflow_id)
        if workflow_status and "overall_progress" in workflow_status:
            progress = workflow_status["overall_progress"]
            print(f"   📊 Progreso: {progress:.0%}")

            if "tasks" in workflow_status:
                print(f"   📝 Tareas: {len(workflow_status['tasks'])} configuradas")

    except Exception as e:
        print(f"❌ Error creando sistema: {e}")


async def show_final_statistics(orchestrator):
    """Muestra estadísticas finales del sistema"""
    print("\n" + "=" * 40)
    print("5. ESTADÍSTICAS FINALES")
    print("=" * 40)

    try:
        status = await orchestrator.get_system_status()

        print(f"\n📈 Métricas del Sistema:")
        metrics = status.get('metrics', {})

        for key, value in metrics.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, float):
                print(f"   • {formatted_key}: {value:.2f}")
            else:
                print(f"   • {formatted_key}: {value}")

        print(f"\n🤖 Agentes Especializados:")
        agents_by_specialty = status['specialized_agents'].get('by_specialty', {})

        for specialty, count in agents_by_specialty.items():
            formatted_specialty = specialty.replace('_', ' ').title()
            print(f"   • {formatted_specialty}: {count}")

        print(f"\n🔄 Estado de Servicios:")
        azure_services = status.get('azure_services', {})

        for service, configured in azure_services.items():
            status_icon = "✅" if configured else "❌"
            formatted_service = service.replace('_', ' ').title()
            print(f"   • {formatted_service}: {status_icon}")

        # Obtener estadísticas de agentes especializados
        agent_stats = await get_agent_statistics(orchestrator)
        if agent_stats:
            print(f"\n📊 Estadísticas de Agentes:")
            for agent_type, stats in agent_stats.items():
                print(f"   • {agent_type}:")
                for stat_name, stat_value in stats.items():
                    if isinstance(stat_value, (int, float)) and stat_name != 'agent_id':
                        print(f"     - {stat_name.replace('_', ' ').title()}: {stat_value}")

    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")


async def get_agent_statistics(orchestrator):
    """Obtiene estadísticas de agentes especializados"""
    try:
        # En una implementación real, esto consultaría cada agente
        # Por ahora, simulamos algunas estadísticas
        return {
            "NextJS Developer": {
                "projects_created": 1,
                "components_generated": 5,
                "apis_implemented": 4,
                "builds_successful": 1
            },
            "Azure Form Recognizer": {
                "documents_processed": 2,
                "successful_extractions": 2,
                "average_confidence": 0.92,
                "azure_api_calls": 2
            },
            "Authentication Security": {
                "users_registered": 2,
                "successful_logins": 1,
                "tokens_issued": 1,
                "audit_logs_created": 8
            }
        }

    except Exception as e:
        logging.error(f"Error obteniendo estadísticas de agentes: {e}")
        return {}


async def interactive_demo():
    """Demostración interactiva donde el usuario puede ingresar comandos"""
    print("\n" + "=" * 40)
    print("MODO INTERACTIVO")
    print("=" * 40)
    print("Ingresa comandos para que SIAME los procese.")
    print("Escribe 'salir' para terminar.\n")

    orchestrator = SiameOrchestrator()
    await orchestrator.initialize()

    try:
        while True:
            try:
                command = input("SIAME> ").strip()

                if command.lower() in ['salir', 'exit', 'quit']:
                    break

                if not command:
                    continue

                print(f"Procesando: {command}")
                result = await orchestrator.process_command(command, SecurityLevel.PUBLIC)
                print(f"Resultado: {result}\n")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}\n")

    finally:
        await orchestrator.shutdown()


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="SIAME 2026v3 Orchestrator Demo")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Ejecutar en modo interactivo")

    args = parser.parse_args()

    if args.interactive:
        asyncio.run(interactive_demo())
    else:
        asyncio.run(demo_orchestrator_usage())


if __name__ == "__main__":
    main()