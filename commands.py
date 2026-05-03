import typer
import json
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from tools.reader import CodeReader
from tools.parser import get_code_structure
from memory.graph_manager import MemoryManager
from tools.registry import AVAILABLE_TOOLS

console = Console()
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

def index_project(path: str = typer.Argument(".", help="Ruta a indexar")):
    """
    Indexa los archivos del proyecto y crea las relaciones.
    """
    console.print(f"[bold blue]Indexando el proyecto en {path}...[/bold blue]")
    memory = MemoryManager()
    reader = CodeReader(path)
    files = reader.list_files()

    for file in files:
        if file.endswith(".py"):
            content = reader.read_file(file)
            structure = get_code_structure(content)
            
            memory.graph.add_node(file, type="file")
            
            for imp in structure["imports"]:
                for target_file in files:
                    module_target = target_file.replace(".py", "").replace("/", ".").replace("\\", ".")
                    file_name_only = target_file.replace("\\", "/").split("/")[-1].replace(".py", "")
                    
                    if (module_target in imp or f"'{file_name_only}'" in imp) and file != target_file:
                        memory.add_relationship(file, target_file, "imports")
    
    memory.save_to_disk()
    console.print("[bold green]¡Indexación terminada y guardada en memory.db![/bold green]")
    return memory

def analyze(file: str):
    """
    Analiza qué archivos se verían afectados si cambias el archivo dado.
    """
    memory = MemoryManager()
    memory.load_from_disk()
    related = memory.get_related_nodes(file)
    
    if not related:
        console.print(f"[yellow]No se encontraron dependencias para {file}[/yellow]")
    else:
        console.print(f"[bold green]Si cambias {file}, podrías afectar a:[/bold green]")
        for item in related:
            console.print(f"🔗 {item}")

def chat(
    prompt: str = typer.Argument(..., help="Lo que quieres preguntarle al agente"),
    model: str = typer.Option("gemma4", help="Modelo a usar (ej: gemma2, llama3)")
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
        
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print("\n")

    except Exception as e:
        console.print(f"[bold red]Error conectando con el modelo:[/bold red] {e}")
        console.print("[yellow]Asegúrate de que Ollama esté corriendo (`ollama serve`)[/yellow]")

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

def run(
    prompt: str = typer.Argument(..., help="Tarea que ejecutará el agente mediante herramientas"),
    model: str = typer.Option("gemma4", help="Modelo a usar")
):
    """
    Inicia un bucle donde el agente puede pensar, decidir y usar herramientas sobre tu código.
    """
    console.print(f"[bold blue]Iniciando agente con la tarea:[/bold blue] {prompt}")
    run_agent_loop(prompt, model=model)

def run_agent_loop(user_prompt: str, model: str = "gemma4"):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}]
    
    for i in range(7):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={ "type": "json_object" }
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
                result = AVAILABLE_TOOLSherramienta
                
                messages.append({"role": "assistant", "content": raw_output})
                messages.append({"role": "system", "content": f"RESULTADO: {result}"})
            
        except Exception as e:
            error_msg = f"Error en el formato o ejecución: {str(e)}"
            messages.append({"role": "system", "content": error_msg})
            console.print(f"[red]{error_msg}[/red]")