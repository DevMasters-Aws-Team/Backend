# KIRO Developer Guide: MCP, SSE Streaming & Comando Cheatsheet

Este documento sirve como la **Guía del Desarrollador de KIRO** para la implementación de servidores **MCP (Model Context Protocol)**, el consumo de la API de **Streaming por Server-Sent Events (SSE)** desde el Frontend, y el catálogo de comandos y atajos de desarrollo para operar tu backend.

---

## 1. Implementación de MCP (Model Context Protocol) en KIRO

El **Pilar 3: MCP** establece que los agentes interactúan con el mundo físico (AWS, Bases de Datos, Repositorios) mediante conectores estandarizados llamados herramientas MCP.

### Ejemplo Base: Registro de una Herramienta MCP en el Agente
Para añadir una nueva herramienta que permita al agente consultar o interactuar con AWS u otros servicios, se sigue este patrón de diseño estructurado:

```python
# kiro_agent/agent.py (Patrón de diseño para MCP)

class MiServicioMcpServer:
    """Servidor MCP para herramientas personalizadas."""

    def registrar_herramientas(self) -> list:
        """Define el esquema JSON que el LLM (Bedrock) entenderá para usar la herramienta."""
        return [
            {
                "name": "obtener_estado_base_datos",
                "description": "Consulta el estado de salud físico de la base de datos de pagos en AWS RDS.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "db_identifier": {"type": "string", "description": "ID de la instancia de base de datos RDS."}
                    },
                    "required": ["db_identifier"]
                }
            }
        ]

    def ejecutar_herramienta(self, tool_name: str, arguments: dict) -> dict:
        """Ejecuta la acción física basada en la decisión del LLM."""
        if tool_name == "obtener_estado_base_datos":
            db_id = arguments.get("db_identifier")
            # Código físico de conexión (ej: boto3.client('rds').describe_db_instances)
            return {
                "status": "healthy",
                "connections": 42,
                "latency_ms": 12
            }
        raise ValueError(f"Herramienta {tool_name} no encontrada.")
```

---

## 2. Flujo de Conexión de Streaming SSE (Server-Sent Events)

El frontend (`kiro-front`) debe consumir el diagnóstico de forma progresiva. En lugar de usar WebSockets (que añaden sobrecarga y complejidad bidireccional), **KIRO utiliza Server-Sent Events (SSE)** sobre HTTP para enviar eventos asíncronos unidireccionales de forma súper ligera.

### Arquitectura de Conexión SSE
```
  [kiro-front (Browser)]                           [kiro-agent (FastAPI)]
           │                                                 │
           │─────── GET /stream_diagnose?trace_id=123 ──────>│ (Inicializa SSE)
           │                                                 │
           │<────── data: {"step": "1. Iniciar Spec"} ───────│ (Evento enviado)
           │                                                 │
           │<────── data: {"step": "2. Analizar MCPs"} ──────│ (Ejecución asíncrona)
           │                                                 │
           │<────── data: {"step": "3. RCA Finalizado"} ─────│ (Reporte y costo USD)
           │                                                 │
           ❌ (Conexión cerrada por el Servidor)              ❌
```

### Código JavaScript para conectar `kiro-front` al Backend
Inserta este código en tu frontend (`kiro-front`) para escuchar los eventos en tiempo real:

```javascript
// kiro-front/src/app.js - Consumo de SSE de KIRO

const traceId = "1-5f3e2e4a-1234567890abcdef12345678";
const sseUrl = `http://localhost:8080/stream_diagnose?trace_id=${traceId}`;

// Inicializar el escuchador de eventos de KIRO
const eventSource = new EventSource(sseUrl);

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log("Evento KIRO Recibido:", data);

    if (data.error) {
        console.error("Fallo en el diagnóstico:", data.error);
        eventSource.close();
        return;
    }

    // Actualizar la interfaz del frontend dinámicamente
    actualizarInterfazProgreso(data.step, data.message || data.result);

    if (data.step === "3. Finalizado") {
        console.log("Diagnóstico completo. Cerrando canal SSE.");
        eventSource.close(); // Cerrar conexión de forma limpia
    }
};

eventSource.onerror = (error) => {
    console.error("Error en conexión SSE de KIRO:", error);
    eventSource.close();
};

function actualizarInterfazProgreso(step, info) {
    // Aquí actualizas tu componente UI (ej: React, Vue, o HTML Vanilla)
    document.getElementById("progress-status").innerText = step;
    if (info.rca_report) {
        document.getElementById("rca-container").innerHTML = `
            <h3>Causa Raíz:</h3>
            <p>${info.rca_report.rca_summary}</p>
            <strong>Coste Estimado de Análisis:</strong> $${info.rca_report.cost_assessment.estimated_cost_usd} USD
        `;
    }
}
```

---

## 3. Catálogo de Comandos y Atajos (Dev Cheatsheet)

Para agilizar el desarrollo y la preparación de demostraciones, utiliza los siguientes atajos definidos en tu entorno:

### Operaciones Locales (`Makefile`)

| Comando | Acción del Desarrollador | Cuándo usarlo |
| :--- | :--- | :--- |
| **`make install`** | Instala todas las dependencias y crea el entorno virtual Poetry. | Al clonar o iniciar el proyecto por primera vez. |
| **`make dev`** | Lanza el servidor de desarrollo FastAPI en `localhost:8080` con auto-reload. | Durante la programación de lógica de agentes y pruebas en vivo. |
| **`make test`** | Ejecuta la suite de pruebas locales (o muestra el estado del esqueleto). | Para verificar que no existan errores de sintaxis o de importación. |
| **`make clean`** | Remueve cachés de Python (`__pycache__`), caches de pruebas, etc. | Para limpiar el espacio de trabajo antes de un commit de Git. |

### Operaciones con Docker y Despliegue

| Comando | Acción del Desarrollador | Cuándo usarlo |
| :--- | :--- | :--- |
| **`make docker-build`** | Construye la imagen Docker del agente (`template-agent:latest`) de forma optimizada. | Para validar el empaquetado del contenedor antes de subirlo a AWS ECR. |
| **`make docker-run`** | Lanza el contenedor de forma local cargando automáticamente tu archivo `.env`. | Para realizar pruebas de integración que emulan el entorno de producción. |

---

## 4. Conexión a AWS Bedrock (Nova / Claude)

Cuando configures tu agente para pasar de simulaciones locales (Mocks) a llamadas de producción reales de inteligencia artificial, tu archivo `.env` debe incluir la autenticación correspondiente:

```ini
# Configuración del Cliente de AWS Bedrock
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=tu_aws_access_key_id
AWS_SECRET_ACCESS_KEY=tu_aws_secret_access_key

# Configuración del Presupuesto de Steering de KIRO
KIRO_MAX_DOLLARS_BUDGET=2.50
KIRO_MAX_CLOUDWATCH_QUERIES=20
```

### Atajo de Código para invocar Modelos de Bedrock en tu Agente:
```python
import boto3
import json

def invocar_bedrock_nova(prompt_sistema: str, prompt_usuario: str) -> str:
    """Invocación directa a Amazon Bedrock usando Amazon Nova Pro."""
    client = boto3.client('bedrock-runtime', region_name='us-east-1')
    
    body = json.dumps({
        "system": [{"text": prompt_sistema}],
        "messages": [{"role": "user", "content": [{"text": prompt_usuario}]}],
        "inferenceConfig": {"temperature": 0.2, "maxTokens": 2000}
    })
    
    response = client.invoke_model(
        modelId="amazon.nova-pro-v1:0", # ID oficial del modelo Nova Pro de Amazon
        body=body
    )
    
    response_body = json.loads(response.get('body').read())
    return response_body['output']['message']['content'][0]['text']
```
*(Este snippet representa la conexión oficial de Bedrock para cuando expandas el archivo [kiro_agent/main.py](file:///C:/Users/USER/Desktop/KIRO%20-%20DEV/kiro-agent/kiro_agent/main.py) con llamadas de IA reales).*
