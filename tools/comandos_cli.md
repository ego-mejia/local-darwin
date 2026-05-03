# Comandos del CLI - Local Darwin

Aquí tienes una breve explicación de los comandos de terminal implementados hasta ahora en el proyecto, ejecutables a través de Typer y `uv`:

## 1. `chat`

**Uso:** `uv run main.py chat "Tu mensaje aquí"`
**Descripción:** Envía una consulta simple a tu modelo local (configurado para usar `gemma4` a través de Ollama) y devuelve la respuesta del Agente en tiempo real (streaming) directamente en la terminal.

## 2. `inspect`

**Uso:** `uv run main.py inspect <ruta>` (ej. `uv run main.py inspect .`)
**Descripción:** Explora el sistema de archivos en la ruta dada. Analiza la estructura de los archivos soportados (Python vía AST) y lista qué clases y funciones están definidas dentro de cada uno, sin necesidad de leer el texto plano completo.

## 3. `index`

**Uso:** `uv run main.py index <ruta>` (ej. `uv run main.py index .`)
**Descripción:** Lee todos los archivos relevantes del proyecto (respetando las reglas de exclusión en `.darwinignore`), extrae sus importaciones y construye un grafo estructurado de relaciones utilizando NetworkX. El resultado se persiste en SQLite (`memory.db`).

## 4. `analyze`

**Uso:** `uv run main.py analyze <archivo>` (ej. `uv run main.py analyze main.py`)
**Descripción:** Consulta la "memoria" del proyecto guardada en `memory.db` y te muestra qué archivos se verían afectados (dependencias y relaciones) si decides modificar el archivo indicado.

## 5. `run`

**Uso:** `uv run main.py run "Tarea"` (ej. `uv run main.py run "Crea un archivo test_suma.py..."`)
**Descripción:** Inicia el bucle de razonamiento del Agente. Evalúa la tarea solicitada, decide qué herramientas usar (como leer/escribir archivos o ejecutar comandos de sistema), ejecuta las herramientas (pidiendo tu confirmación cuando sea necesario) y devuelve un resultado final basado en la interacción directa con tu código.

---

_Nota: Es importante ejecutar `index` periódicamente o cuando haya cambios grandes en la estructura del proyecto para que `analyze` trabaje con información actualizada._
