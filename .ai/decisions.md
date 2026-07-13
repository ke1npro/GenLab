# Decisions — GenLab

Registro de decisiones importantes. Formato: Fecha / Problema / Opciones / Decisión / Justificación / Impacto.

---

## D1 — Separación Provider / Model Manager
- **Fecha**: 2026-07-13
- **Problema**: ¿El Provider debe gestionar descarga/versión/caché de pesos o solo inferencia?
- **Opciones**:
  A. Provider hace todo (descarga + infiere).
  B. Separar: Provider infiere, ModelManager gestiona pesos.
- **Decisión**: B. Provider = solo inferencia; ModelManager = ciclo de vida (MVP: `ensure/get_info/clear_cache`).
- **Justificación**: A viola responsabilidad única y duplica `snapshot_download` en cada modelo. B evita reescritura al crecer.
- **Impacto**: Contrato del Provider más limpio; Manager reutilizable por todos los modelos.

## D2 — Pipeline diseñado antes que el primer Provider
- **Fecha**: 2026-07-13
- **Problema**: ¿Construir CogVideoX primero o fijar el Pipeline primero?
- **Opciones**:
  A. Implementar provider y luego extraer contrato.
  B. Fijar contrato de steps + orchestrator, luego implementar provider contra él.
- **Decisión**: B (Hito 1.4 antes de 1.5).
- **Justificación**: El Provider se define por lo que el Pipeline necesita; hacerlo al revés casi garantiza rehacer la interfaz.
- **Impacto**: Menos reorganizaciones; el Pipeline es el corazón estable.

## D3 — Configuración por perfiles con precedencia
- **Fecha**: 2026-07-13
- **Problema**: ¿Cómo cambiar params (res/dtype/steps) sin editar código y sin repetir?
- **Opciones**:
  A. Solo YAML por modelo.
  B. Precedencia `default < modelo < perfil < args` + mecanismo en MVP, perfiles concretos en Beta.
- **Decisión**: B.
- **Justificación**: El mecanismo es barato y evita reescribir el loader después; los perfiles son solo datos.
- **Impacto**: Cambio de calidad/VRAM = seleccionar perfil, no tocar muchos parámetros.

## D4 — API REST diferida a v1.0
- **Fecha**: 2026-07-13
- **Problema**: ¿API REST en Beta o más tarde?
- **Opciones**:
  A. API en Beta.
  B. API en v1.0 (reusa orchestrator).
- **Decisión**: B.
- **Justificación**: No se usará pronto; reusa el mismo orchestrator, así que no genera deuda diferirla. Solo mantener orchestrator agnóstico de interfaz.
- **Impacto**: Menos trabajo en Beta; sin riesgo de acoplamiento.

## D5 — Sistema de Plugins diferido a post-v1.0
- **Fecha**: 2026-07-13
- **Problema**: ¿Plugins formales en v1.0?
- **Opciones**:
  A. Plugins en v1.0.
  B. Diferir; diseñar registry entry-point friendly ahora.
- **Decisión**: B.
- **Justificación**: El 90% del valor (nuevo modelo = archivo + decorador) ya lo da el registry. Plugins formales solo pagan con terceros contribuyendo.
- **Impacto**: Menos sobre-ingeniería; migración a plugins será capa fina.

## D6 — Task Registry mínimo
- **Fecha**: 2026-07-13
- **Problema**: ¿Registry de Tasks necesario o bastan capabilities del Provider?
- **Opciones**:
  A. Sin registry; dispatch por capabilities.
  B. Registry mínimo (dict nombre→clase Task) en MVP, enriquecer en Beta.
- **Decisión**: B.
- **Justificación**: Capabilities dicen *qué puede* el modelo, no *cómo se hace* la tarea (preprocesado/postprocesado). El registry desacopla intención de modelo y facilita dispatch futuro.
- **Impacto**: Un hueso de registry ahora, carne (metadatos, default por tarea) en Beta.

## D7 — Manifest por generación + captura benchmark en MVP
- **Fecha**: 2026-07-13
- **Problema**: ¿Capturar metadata de ejecución desde MVP o después?
- **Opciones**:
  A. Manifest en Beta.
  B. Manifest JSON en MVP (modelo, seed, steps, resolución, tiempo, gpu, perfil).
- **Decisión**: B. La herramienta de comparación de benchmarks queda en Beta (2.5).
- **Justificación**: El manifest es casi gratis y satisface reproducibilidad + alimenta benchmark.
- **Impacto**: Reproducir cualquier video meses después; datos de benchmark sin coste extra.

## D8 — Bootstrap con reporte diagnóstico
- **Fecha**: 2026-07-13
- **Problema**: ¿Solo preparar entorno o también reportar estado?
- **Opciones**:
  A. Bootstrap silencioso.
  B. Bootstrap + reporte (GPU, VRAM, RAM, Drive, Internet, HF, CUDA, espacio, caché).
- **Decisión**: B.
- **Justificación**: La detección ya es necesaria para funcionar; imprimirla cuesta ~30 líneas y facilita diagnóstico sin leer logs.
- **Impacto**: Detección de problemas en segundos desde el MVP.

## D9 — Aplanamiento de overrides en PrepareInputsStep
- **Fecha**: 2026-07-13
- **Problema**: El usuario pasa `config={'model': {'steps': 50}}` pero `task.prepare_inputs()` espera `steps=50` a nivel plano.
- **Opciones**:
  A. El usuario pasa parámetros planos directamente.
  B. El step extrae el namespace `model` de los overrides y lo mergea con la config del modelo antes de pasarlo a prepare_inputs().
- **Decisión**: B.
- **Justificación**: La API `config={'model': {...}}` es consistente con la estructura YAML; el aplanamiento es transparente y no requiere que el usuario conozca la estructura interna del task.
- **Impacto**: La API pública es más natural; el step es responsable de la transformación.

## D10 — Dependencias pesadas como opcionales
- **Fecha**: 2026-07-13
- **Problema**: torch + diffusers suman >2GB, inviables para instalación local si solo se edita config.
- **Opciones**:
  A. Todas las deps en `dependencies` de pyproject.toml.
  B. Core mínimo (`pyyaml`, `psutil`) en `dependencies`; torch/diffusers/imageio como extras `[gpu]` y `[video]`.
- **Decisión**: B.
- **Justificación**: Permite `pip install genlab` ligero para editar YAML/tests; `pip install genlab[all]` en Colab.
- **Impacto**: pyproject.toml más verboso pero instalación local ágil.

## D11 — Entorno como capa de precedencia
- **Fecha**: 2026-07-13
- **Problema**: Los YAML de `environments/colab.yaml` y `local.yaml` existían pero nunca se cargaban.
- **Opciones**:
  A. Ignorarlos; la detección de paths está en Python.
  B. Cargarlos como capa de precedencia entre default y modelo.
- **Decisión**: B.
- **Justificación**: Consistencia con el diseño documentado; permite sobrescribir params por entorno sin tocar Python.
- **Impacto**: La precedencia ahora es `default < env < modelo < perfil < args`.
