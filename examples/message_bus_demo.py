#!/usr/bin/env python3
"""
SIAME 2026v3 - Message Bus Demo
Demostración del sistema de comunicación entre subagentes

Este ejemplo muestra:
- Registro de agentes en el message bus
- Comunicación asíncrona entre agentes
- Sistema de eventos pub/sub
- Manejo de errores y reintentos
- Contexto compartido entre agentes
- Monitoreo del sistema
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Agregar path del proyecto
sys.path.append(str(Path(__file__).parent.parent))

from shared.communication.message_bus import (
    MessageBus, Task, Event, EventType, MessagePriority,
    AgentContext, get_message_bus
)


class ExampleAgent:
    """Agente de ejemplo que usa el message bus"""

    def __init__(self, agent_id: str, agent_type: str, name: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.message_bus = None
        self.is_running = False
        self.processed_tasks = 0

    async def start(self, message_bus: MessageBus):
        """Inicia el agente y se conecta al message bus"""
        self.message_bus = message_bus
        self.is_running = True

        # Registrar agente
        success = await self.message_bus.register_agent(
            self.agent_id,
            self.agent_type,
            self.name,
            capabilities=["document_processing", "data_analysis"]
        )

        if success:
            print(f"✅ Agente {self.name} registrado exitosamente")

            # Suscribirse a eventos
            await self.message_bus.subscribe_to_events("*", self._handle_event)

            # Iniciar worker para procesar tareas
            asyncio.create_task(self._task_worker())
            asyncio.create_task(self._heartbeat_sender())

        return success

    async def stop(self):
        """Detiene el agente"""
        self.is_running = False
        if self.message_bus:
            await self.message_bus.unregister_agent(self.agent_id)
            print(f"🔴 Agente {self.name} desconectado")

    async def _task_worker(self):
        """Worker que procesa tareas asignadas al agente"""
        while self.is_running:
            try:
                # Simular procesamiento de tareas
                # En un agente real, esto escucharía mensajes específicos
                await asyncio.sleep(1)

                # Actualizar estado
                await self.message_bus.update_agent_status(
                    self.agent_id,
                    "active",
                    {"tasks_processed": self.processed_tasks}
                )

            except Exception as e:
                print(f"❌ Error en worker de {self.name}: {e}")
                await asyncio.sleep(5)

    async def _heartbeat_sender(self):
        """Envía heartbeats al message bus"""
        while self.is_running:
            try:
                await self.message_bus.update_agent_status(
                    self.agent_id,
                    "active",
                    {"last_heartbeat": datetime.now()}
                )
                await asyncio.sleep(30)  # Heartbeat cada 30 segundos

            except Exception as e:
                print(f"❌ Error enviando heartbeat de {self.name}: {e}")
                await asyncio.sleep(30)

    async def _handle_event(self, event: Event):
        """Maneja eventos del sistema"""
        if event.source_agent_id != self.agent_id:  # No procesar eventos propios
            print(f"📢 {self.name} recibió evento: {event.event_type.value} de {event.source_agent_id}")

    async def process_task(self, task: Task) -> dict:
        """Procesa una tarea específica"""
        try:
            print(f"🔄 {self.name} procesando tarea: {task.task_type}")

            # Simular procesamiento
            await asyncio.sleep(2)

            # Simular posibilidad de error (10% de probabilidad)
            import random
            if random.random() < 0.1:
                raise Exception(f"Error simulado en {self.name}")

            self.processed_tasks += 1

            result = {
                "status": "completed",
                "agent": self.name,
                "processed_at": datetime.now().isoformat(),
                "result_data": f"Resultado procesado por {self.name}"
            }

            print(f"✅ {self.name} completó tarea: {task.id}")
            return result

        except Exception as e:
            print(f"❌ {self.name} falló tarea {task.id}: {e}")
            raise


async def demo_basic_messaging():
    """Demostración básica del message bus"""
    print("\n" + "="*50)
    print("DEMO: Comunicación Básica entre Agentes")
    print("="*50)

    # Crear message bus
    message_bus = get_message_bus({
        "queue_max_size": 100,
        "max_retry_delay": 30
    })

    try:
        # Inicializar message bus
        await message_bus.initialize()
        print("🚀 Message Bus inicializado")

        # Crear agentes de ejemplo
        agents = [
            ExampleAgent("agent_1", "document_processor", "Procesador de Documentos"),
            ExampleAgent("agent_2", "data_analyzer", "Analizador de Datos"),
            ExampleAgent("agent_3", "form_recognizer", "Reconocedor de Formularios")
        ]

        # Iniciar agentes
        for agent in agents:
            await agent.start(message_bus)
            await asyncio.sleep(0.5)

        # Mostrar agentes disponibles
        print("\n📋 Agentes disponibles:")
        available_agents = await message_bus.get_available_agents()
        for agent in available_agents:
            print(f"   • {agent.agent_name} ({agent.agent_type}) - Estado: {agent.status}")

        # Esperar un momento para que se establezcan las conexiones
        await asyncio.sleep(2)

        # Crear y enviar tareas de ejemplo
        tasks = [
            Task(
                task_type="process_document",
                description="Procesar hoja de remisión OGA",
                agent_type="document_processor",
                input_data={"document_type": "hoja_oga", "file_path": "/tmp/doc1.pdf"},
                priority=MessagePriority.HIGH
            ),
            Task(
                task_type="analyze_data",
                description="Analizar datos extraídos",
                agent_type="data_analyzer",
                input_data={"data_source": "extracted_fields"},
                priority=MessagePriority.NORMAL
            ),
            Task(
                task_type="recognize_form",
                description="Reconocer formulario con Azure",
                agent_type="form_recognizer",
                input_data={"azure_config": {"model": "custom"}},
                priority=MessagePriority.CRITICAL
            )
        ]

        print("\n📤 Enviando tareas...")
        for task in tasks:
            success = await message_bus.submit_task(task)
            if success:
                print(f"   ✅ Tarea enviada: {task.description}")
            else:
                print(f"   ❌ Error enviando tarea: {task.description}")

        # Simular procesamiento de tareas
        print("\n⏳ Simulando procesamiento de tareas...")
        for i, task in enumerate(tasks):
            try:
                # Seleccionar agente apropiado
                available = await message_bus.get_available_agents(task.agent_type)
                if available:
                    selected_agent = available[0]
                    agent_obj = next((a for a in agents if a.agent_id == selected_agent.agent_id), None)

                    if agent_obj:
                        result = await agent_obj.process_task(task)
                        await message_bus.complete_task(task.id, result, agent_obj.agent_id)
                    else:
                        print(f"⚠️  No se encontró objeto agente para {selected_agent.agent_id}")
                else:
                    print(f"⚠️  No hay agentes disponibles para tipo: {task.agent_type}")

            except Exception as e:
                await message_bus.fail_task(task.id, e, "system")

        await asyncio.sleep(2)

        # Mostrar estadísticas
        stats = await message_bus.get_system_statistics()
        print(f"\n📊 Estadísticas del Sistema:")
        print(f"   • Total de mensajes: {stats['global_stats']['total_messages']}")
        print(f"   • Total de tareas: {stats['global_stats']['total_tasks']}")
        print(f"   • Total de eventos: {stats['global_stats']['total_events']}")
        print(f"   • Agentes activos: {stats['context_stats']['active_agents']}")
        print(f"   • Tareas activas: {stats['active_tasks']}")

        # Parar agentes
        print("\n🔄 Deteniendo agentes...")
        for agent in agents:
            await agent.stop()

        await asyncio.sleep(1)

    finally:
        await message_bus.shutdown()


async def demo_event_system():
    """Demostración del sistema de eventos"""
    print("\n" + "="*50)
    print("DEMO: Sistema de Eventos Pub/Sub")
    print("="*50)

    message_bus = get_message_bus()
    await message_bus.initialize()

    try:
        # Contador de eventos recibidos
        events_received = {"count": 0}

        # Handler de eventos
        async def event_logger(event: Event):
            events_received["count"] += 1
            print(f"🔔 Evento #{events_received['count']}: {event.event_type.value}")
            print(f"   Fuente: {event.source_agent_id}")
            print(f"   Severidad: {event.severity}")
            print(f"   Datos: {event.event_data}")
            print()

        # Suscribirse a todos los eventos
        await message_bus.subscribe_to_events("*", event_logger)

        # Registrar un agente
        await message_bus.register_agent(
            "demo_agent",
            "demo_type",
            "Agente de Demostración"
        )

        # Publicar eventos de ejemplo
        events = [
            Event(
                event_type=EventType.DOCUMENT_PROCESSED,
                source_agent_id="demo_agent",
                event_data={"document_id": "doc_001", "processing_time": 2.5},
                severity="info"
            ),
            Event(
                event_type=EventType.SECURITY_ALERT,
                source_agent_id="security_agent",
                event_data={"alert_type": "unauthorized_access", "user_id": "unknown"},
                severity="warning"
            ),
            Event(
                event_type=EventType.SYSTEM_ERROR,
                source_agent_id="system",
                event_data={"error_code": "DB_CONNECTION_FAILED", "details": "Connection timeout"},
                severity="error"
            )
        ]

        print("📡 Publicando eventos...")
        for event in events:
            delivered = await message_bus.publish_event(event)
            print(f"   Evento {event.event_type.value} entregado a {delivered} suscriptores")

        await asyncio.sleep(1)

        print(f"\n📈 Total de eventos procesados: {events_received['count']}")

    finally:
        await message_bus.shutdown()


async def demo_error_handling():
    """Demostración del manejo de errores y reintentos"""
    print("\n" + "="*50)
    print("DEMO: Manejo de Errores y Reintentos")
    print("="*50)

    message_bus = get_message_bus()
    await message_bus.initialize()

    try:
        # Crear agente que falla intencionalmente
        class FailingAgent(ExampleAgent):
            def __init__(self):
                super().__init__("failing_agent", "failer", "Agente que Falla")
                self.attempt_count = 0

            async def process_task(self, task: Task) -> dict:
                self.attempt_count += 1
                print(f"🔄 Intento #{self.attempt_count} de procesar tarea {task.id}")

                # Fallar en los primeros 2 intentos, éxito en el 3ro
                if self.attempt_count < 3:
                    raise Exception(f"Fallo simulado - intento {self.attempt_count}")

                print(f"✅ Tarea exitosa en el intento {self.attempt_count}")
                return {"status": "success", "attempts": self.attempt_count}

        # Iniciar agente
        failing_agent = FailingAgent()
        await failing_agent.start(message_bus)

        # Crear tarea que fallará inicialmente
        task = Task(
            task_type="failing_task",
            description="Tarea que falla pero se recupera",
            agent_type="failer",
            max_retries=3
        )

        print("📤 Enviando tarea que fallará...")
        await message_bus.submit_task(task)

        # Simular varios intentos
        for attempt in range(4):
            try:
                print(f"\n--- Intento {attempt + 1} ---")
                result = await failing_agent.process_task(task)
                await message_bus.complete_task(task.id, result, failing_agent.agent_id)
                print("🎉 Tarea completada exitosamente!")
                break

            except Exception as e:
                print(f"❌ Fallo: {e}")
                await message_bus.fail_task(task.id, e, failing_agent.agent_id)

                if attempt < 3:
                    print("⏳ Esperando antes del siguiente intento...")
                    await asyncio.sleep(2)

        # Mostrar estadísticas de errores
        stats = await message_bus.get_system_statistics()
        error_stats = stats.get("error_stats", {})
        print(f"\n📊 Estadísticas de Errores:")
        print(f"   • Tareas fallidas: {error_stats.get('failed_tasks_count', 0)}")
        print(f"   • Reintentos pendientes: {error_stats.get('pending_retries', 0)}")
        print(f"   • Total de errores: {error_stats.get('total_errors', 0)}")

        await failing_agent.stop()

    finally:
        await message_bus.shutdown()


async def demo_shared_context():
    """Demostración del contexto compartido"""
    print("\n" + "="*50)
    print("DEMO: Contexto Compartido entre Agentes")
    print("="*50)

    message_bus = get_message_bus()
    await message_bus.initialize()

    try:
        # Crear varios agentes
        agents = []
        for i in range(3):
            agent = ExampleAgent(f"context_agent_{i}", "context_demo", f"Agente Contexto {i}")
            await agent.start(message_bus)
            agents.append(agent)

        # Establecer estado global
        await message_bus.set_global_state("demo_setting", "valor_compartido")
        await message_bus.set_global_state("processing_mode", "batch")
        await message_bus.set_global_state("max_concurrent_tasks", 5)

        print("🌐 Estado global establecido")

        # Cada agente lee el estado global
        for agent in agents:
            demo_setting = await message_bus.get_global_state("demo_setting")
            processing_mode = await message_bus.get_global_state("processing_mode")

            print(f"📖 {agent.name} leyó:")
            print(f"   demo_setting: {demo_setting}")
            print(f"   processing_mode: {processing_mode}")

        # Actualizar estado de workflow compartido
        workflow_id = "demo_workflow_001"
        await message_bus.shared_context.update_workflow_state(workflow_id, {
            "status": "in_progress",
            "completed_tasks": 3,
            "total_tasks": 10,
            "current_stage": "processing"
        })

        print(f"\n🔄 Estado de workflow {workflow_id} actualizado")

        # Leer estado de workflow
        workflow_state = await message_bus.shared_context.get_workflow_state(workflow_id)
        print(f"📋 Estado del workflow:")
        for key, value in workflow_state.items():
            print(f"   {key}: {value}")

        # Mostrar información de agentes
        print(f"\n👥 Información de agentes:")
        for agent_id, context in message_bus.shared_context.agents.items():
            print(f"   • {context.agent_name}:")
            print(f"     - Estado: {context.status}")
            print(f"     - Carga: {context.load_factor:.1%}")
            print(f"     - Última señal: {context.last_heartbeat}")

        # Parar agentes
        for agent in agents:
            await agent.stop()

    finally:
        await message_bus.shutdown()


async def main():
    """Función principal que ejecuta todas las demostraciones"""
    print("🎯 SIAME 2026v3 - Demostración del Message Bus")
    print("Sistema Nervioso Central de Comunicación entre Agentes")
    print("=" * 60)

    # Configurar logging
    logging.basicConfig(
        level=logging.WARNING,  # Reducir verbosidad para la demo
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        # Ejecutar demostraciones
        await demo_basic_messaging()
        await asyncio.sleep(1)

        await demo_event_system()
        await asyncio.sleep(1)

        await demo_error_handling()
        await asyncio.sleep(1)

        await demo_shared_context()

        print("\n🎉 Todas las demostraciones completadas exitosamente!")
        print("\nEl Message Bus de SIAME 2026v3 proporciona:")
        print("   ✅ Comunicación asíncrona entre agentes")
        print("   ✅ Sistema de eventos pub/sub")
        print("   ✅ Manejo automático de errores y reintentos")
        print("   ✅ Contexto compartido para coordinación")
        print("   ✅ Monitoreo y estadísticas en tiempo real")
        print("   ✅ Escalabilidad y alta disponibilidad")

    except KeyboardInterrupt:
        print("\n⏹️  Demo interrumpida por usuario")
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        logging.exception("Error en demostración")


if __name__ == "__main__":
    asyncio.run(main())