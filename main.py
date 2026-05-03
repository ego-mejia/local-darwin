import typer
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

# Importa CodeReader y get_code_structure en main.py.
from tools.reader import CodeReader
from tools.parser import get_code_structure
from tools.registry import AVAILABLE_TOOLS

# Configuración inicial
app = typer.Typer(help="Agente de Coding Local - Fase 1")
console = Console()
 
# Cliente para Ollama (o vLLM)
# Por defecto Ollama corre en el puerto 11434
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama no requiere key, pero la librería sí pide un string
)
SYSTEM_PROMPT = """
Eres un Agente de Coding Local de nivel Senior. Tu objetivo es resolver tareas usando tus herramientas.
REGLA DE ORO: Siempre responde en formato JSON.

Formato de respuesta:
{
    "pensamiento": "Tu razonamiento paso a paso",
    "herramienta": "nombre_de_la_herramienta",
    "argumentos": {"arg_name": "valor"},
    "respuesta_final": "Solo si terminaste la tarea"
}

Herramientas disponibles:
- read_file(path): Lee código.
- write_file(path, content): Escribe código.
- execute_command(command): Ejecuta comandos en terminal (ej: pytest, ls).
"""

@app.command()
def chat(
    prompt: str = typer.Argument(..., help="Lo que quieres preguntarle al agente"),
    model: str = typer.Option("gemma4", help="Modelo a usar (ej: gemma2, llama3)") #! utilizando Gemma4
):
    """
    Envía una consulta simple al modelo local.
    """
    console.print(f"[bold blue]Buscando respuesta con {model}...[/bold blue]")
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Eres un ingeniero de software senior experto en desarrollo local."},
                {"role": "user", "content": prompt}
            ],
            stream=True # Activamos stream para que la respuesta fluya
        )

        console.print(Panel.fit("[bold green]Agente:[/bold green]", border_style="green"))
        
        # Procesamos la respuesta en streaming
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print("\n")

    except Exception as e:
        console.print(f"[bold red]Error conectando con el modelo:[/bold red] {e}")
        console.print("[yellow]Asegúrate de que Ollama esté corriendo (`ollama serve`)[/yellow]")

@app.command()
def inspect(path: str = typer.Argument(".", help="Ruta a inspeccionar")):
    """
    Lista los archivos y muestra la estructura del código en la ruta dada.
    """
    reader = CodeReader(path)
    files = reader.list_files()
    
    console.print(f"[bold blue]Archivos encontrados en {path}:[/bold blue]")
    for f in files:
        if f.endswith(".py"):
            content = reader.read_file(f)
            struct = get_code_structure(content)
            console.print(f"📄 [bold]{f}[/bold] -> Clases: {struct['classes']}, Funciones: {struct['functions']}")
        else:
            console.print(f"📄 {f}")

from commands import index_project, analyze

app.command(name="index")(index_project)
app.command(name="analyze")(analyze)

import re

@app.command()
def run(
    prompt: str = typer.Argument(..., help="Tarea que ejecutará el agente mediante herramientas"),
    model: str = typer.Option("gemma4", help="Modelo a usar")
):
    """
    Inicia un bucle donde el agente puede pensar, decidir y usar herramientas sobre tu código.
    """
    console.print(f"[bold blue]Iniciando agente con la tarea:[/bold blue] {prompt}")
    run_agent_loop(prompt, model=model)


import json

def run_agent_loop(user_prompt: str, model: str = "gemma4"):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
    
    for i in range(7): # Un par de pasos más por si acaso
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={ "type": "json_object" } # Si tu backend lo soporta (Ollama lo hace)
        )
        
        raw_output = response.choices[0].message.content
        
        try:
            data = json.loads(raw_output)
            pensamiento = data.get("pensamiento")
            herramienta = data.get("herramienta")
            argumentos = data.get("argumentos")
            final = data.get("respuesta_final")

            console.print(f"\n[bold blue]🤔 Paso {i+1}:[/bold blue] {pensamiento}")

            if final:
                console.print(f"\n[bold green]✅ RESPUESTA FINAL:[/bold green]\n{final}")
                break

            if herramienta and herramienta in AVAILABLE_TOOLS:
                # Ejecutamos la herramienta con los argumentos del JSON
                # Nota: En Python usamos **argumentos para pasar el dict como kwargs
                result = AVAILABLE_TOOLS[herramienta](**argumentos)
                
                messages.append({"role": "assistant", "content": raw_output})
                messages.append({"role": "system", "content": f"RESULTADO: {result}"})
            
        except Exception as e:
            error_msg = f"Error en el formato o ejecución: {str(e)}"
            messages.append({"role": "system", "content": error_msg})
            console.print(f"[red]{error_msg}[/red]")



if __name__ == "__main__":
    app()