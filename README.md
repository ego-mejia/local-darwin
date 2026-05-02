# La Hoja de Ruta (Vista General)

## Etapa 1: El Esqueleto (CLI & Conectividad): Crear la base de Python y lograr que hable con tu modelo local (Ollama/vLLM).

## Etapa 2: La Vista (File System & Parsing): Hacer que el agente pueda "leer" archivos y entender código usando ast (Abstract Syntax Trees) para alimentar el grafo.

## Etapa 3: La Memoria (NetworkX & SQLite): Construir el mapa de relaciones y persistirlo para que el agente no olvide cómo se conectan los archivos.

## Etapa 4: Las Manos (Agente & Tool Use): Implementar la lógica donde el modelo decide: "Voy a leer este archivo, luego a ejecutar este test".

## Etapa 5: El Puente (VSCode Extension): Crear la interfaz para que uses todo esto sin salir de tu editor.

### 🛠️ Fase 1: El Esqueleto

El objetivo de hoy es tener un comando en tu terminal que, al ejecutarlo, le envíe un mensaje a tu LLM local y te devuelva una respuesta profesional.

#### Tarea 1.1: Setup del Entorno. \* Crea una carpeta para el proyecto.

Configura un entorno virtual (recomiendo uv o poetry para manejar dependencias, pero venv está bien).

Instala las librerías base: typer (para el CLI) y openai (la mayoría de los backends locales como Ollama o vLLM usan el estándar de OpenAI).

#### Tarea 1.2: El CLI "Hello Agent".

Crea un archivo main.py.

Usa Typer para crear un comando básico de chat. Ejemplo: python main.py chat "Hola, ¿quién eres?".

#### Tarea 1.3: Conexión con el Modelo Local.

Asegúrate de tener Ollama (o similar) corriendo con un modelo (Gemma 2 o 4).

Configura el cliente en Python para que apunte a localhost:11434.

Logra que el agente responda a tu comando de la Tarea 1.2 usando el modelo local.

# Test

Para lograr comunicarse con el agente desde la terminal:

```
uv run main.py "Agregar aqui el prompt"
# se corre sin utilizar el chat
```

# 👁️ Fase 2: La Vista (File System & Parsing)

El objetivo es que el agente pueda responder a: "¿Qué funciones hay en el archivo auth.py?" sin tener que leer todo el archivo línea por línea manualmente.

En esta fase vamos a darle la capacidad de explorar tu sistema de archivos y, lo más importante, de entender la estructura del código sin simplemente leerlo como texto plano. Para esto usaremos AST (Abstract Syntax Trees).

¿Qué es el AST?

En lugar de ver el código como una cadena de texto, el AST convierte el código en un árbol jerárquico. Esto nos permite saber exactamente dónde empieza una función, qué argumentos recibe y qué otras librerías importa, de forma estructurada.
