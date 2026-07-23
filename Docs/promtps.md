# Contexto del Rol y la Misión
Actúas como un Arquitecto de Software Principal, Staff Engineer y Consultor Full Stack con décadas de experiencia en el diseño de plataformas distribuidas empresariales, observabilidad, DevOps y SRE en AWS.

Tu misión es diseñar la **arquitectura funcional, técnica y detallada de un Agente Inteligente de Observabilidad y Análisis de Logs Multi-Microservicio**, integrado nativamente con **AWS** y construido bajo la **arquitectura conceptual y el framework de KIRO**.

---

## 1. El Desafío de Negocio y Tecnológico (Impacto e Innovación)
La plataforma empresarial cuenta con decenas de microservicios distribuidos que generan un volumen masivo de logs en AWS CloudWatch. El análisis manual de incidentes es lento, reactivo y costoso, lo que eleva el MTTD (Mean Time to Detect) y el MTTR (Mean Time to Resolve).

El objetivo es diseñar una solución basada en **Kiro** que no solo lea logs, sino que actúe como un especialista permanente en observabilidad, correlacionando eventos, analizando la causa raíz (Root Cause Analysis), y consumiendo documentación técnica (OpenAPI, diagramas, ADRs, wikis) para comprender el comportamiento esperado vs. anómalo.

---

## 2. Requerimientos de Diseño Basados en los 5 Pilares de KIRO

Tu propuesta arquitectónica debe estructurarse obligatoriamente integrando los siguientes conceptos clave de KIRO:

### A. STEERING (Dirección y Gobierno del Agente)
*   **Definición de Límites:** Diseña las reglas de comportamiento, políticas de seguridad y límites operativos del agente de observabilidad (evitar bucles infinitos de consulta a AWS, control de costes de API, y protección de datos sensibles/PII en los logs antes de procesarlos).
*   **Modos de Operación:** Describe cómo operará el agente en los modos:
    *   *Auto / Siempre:* Monitoreo proactivo en segundo plano y detección de anomalías en tiempo real.
    *   *Manual / Interactivo:* Cuando un desarrollador solicita un diagnóstico específico sobre una petición (Trace ID).

### B. HOOKS (Ganchos y Conectores de Extensión)
*   **Inyección de Lógica:** Diseña los puntos de extensión (Hooks) del sistema para permitir a los equipos de desarrollo agregar lógica personalizada sin modificar el núcleo del agente.
*   **Ejemplos de Aplicación:** Diseña hooks para:
    *   *Hook de Sanitización:* Enmascaramiento de contraseñas, tokens y PII en tránsito.
    *   *Hook de Notificación:* Enrutamiento inteligente de alertas (Slack, PagerDuty, Jira) según severidad y contexto.
    *   *Hook de Enriquecimiento:* Inyección de metadatos de despliegue (Git commit, versión del servicio) al log analizado.

### C. MCP (Model Context Protocol - Protocolo de Contexto)
*   **Conectividad del Modelo con el Entorno:** Diseña los servidores MCP necesarios para dar acceso seguro y estructurado a los datos externos:
    *   *AWS CloudWatch & X-Ray MCP Server:* Para consultar logs, métricas y trazas en tiempo real de forma estructurada.
    *   *Knowledge Base MCP Server:* Para indexar y consultar documentación técnica (Swagger/OpenAPI, diagramas de arquitectura, contratos, ADRs, READMEs de repositorios).
    *   *AWS Infrastructure MCP Server:* Para consultar el estado de salud de Lambdas, ECS, EKS y API Gateways.

### D. ARQUITECTURA DE AGENTES (Colaboración Multi-Agente)
*   **Ecosistema de Agentes de Kiro:** Define una arquitectura multi-agente donde cada uno tenga "Skills" y responsabilidades bien delimitadas:
    1.  *Agente Coordinador de Incidentes (Orquestador):* Recibe alertas, gestiona el flujo de diagnóstico y consolida el reporte final.
    2.  *Agente Analista de Logs (CloudWatch Specialist):* Especializado en queries complejas de CloudWatch Insights y detección de patrones de error.
    3.  *Agente de Correlación y Trazabilidad (SRE Specialist):* Sigue el flujo del Request ID a través de múltiples microservicios y correlaciona logs.
    4.  *Agente de Contexto de Negocio (Docs Specialist):* Analiza la documentación técnica para validar si el error es un comportamiento anómalo o esperado según el flujo funcional.

### E. SPECS (Especificaciones de Ejecución de Tareas)
*   **Planos Técnicos de Acción:** Define el diseño de las "Specs" (workflows estructurados ejecutables por Kiro) para automatizar la resolución de incidentes:
    *   *Flujo de Spec:* Alerta de error en AWS -> Generación automática de Spec de Diagnóstico (`Wf_Intent_to_Plan`) -> Ejecución secuencial de consultas -> Generación de Reporte RCA y Recomendaciones.

---

## 3. Integración con Servicios de AWS
Detalla cómo la arquitectura interactúa nativamente con el ecosistema de AWS utilizando buenas prácticas de seguridad (IAM Roles, Least Privilege) y rendimiento:
*   **Ingesta de Datos:** Amazon CloudWatch Logs, AWS X-Ray (Trazabilidad), Amazon EventBridge (Disparador de alertas).
*   **Capa de Cómputo/Servicios:** AWS Lambda para procesamiento serverless de hooks, Amazon ECS/EKS como entorno de ejecución de los microservicios, y Amazon Bedrock (o LLMs compatibles) como motor de IA.
*   **Almacenamiento de Documentación:** Amazon S3 / Amazon Kendra como base de conocimiento para recuperar documentos de arquitectura y ADRs de forma semántica (RAG).

---

## 4. Entregables Esperados en tu Respuesta
Como Staff Engineer, tu diseño debe ser extremadamente riguroso y estar estructurado de la siguiente manera:

1.  **Diagrama de Arquitectura Conceptual (en formato Mermaid):** Mostrando la interacción entre la plataforma en AWS, los Servidores MCP de Kiro, la orquestación Multi-Agente, y el sistema de Steering/Hooks.
2.  **Especificación Técnica de los Servidores MCP:** Definición de los endpoints/herramientas que expondrá el protocolo MCP para AWS CloudWatch y la base de conocimiento de documentación.
3.  **Matriz de Agentes, Skills y Comandos:** Detalle de cada agente de Kiro involucrado, sus habilidades específicas, y los `/commands` que soportará para interactuar con el equipo de soporte.
4.  **Flujo Paso a Paso de una "Spec" ante un Incidente:** Simulación detallada de cómo el agente procesa un error crítico (ej. Falla en el checkout de una app) desde que salta la alerta en CloudWatch hasta que genera las recomendaciones técnicas basadas en logs y OpenAPI.
5.  **Análisis de Viabilidad, Rendimiento y Seguridad (Costes en AWS + Latencia):** Propuestas innovadoras para optimizar el consumo de tokens y asegurar que el agente funcione de manera eficiente y escalable en producción.