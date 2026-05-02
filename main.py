import typer
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

# Importa CodeReader y get_code_structure en main.py.
from tools.reader import CodeReader
from tools.parser import get_code_structure

# Configuración inicial
app = typer.Typer(help="Agente de Coding Local - Fase 1")
console = Console()
 
# Cliente para Ollama (o vLLM)
# Por defecto Ollama corre en el puerto 11434
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Ollama no requiere key, pero la librería sí pide un string
)

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

# Connect Parser with Graph Manager
# Lógica conceptual para tu comando de indexación
def index_project(path: str):
    memory = MemoryManager()
    reader = CodeReader(path)
    files = reader.list_files()

    for file in files:
        if file.endswith(".py"):
            content = reader.read_file(file)
            structure = get_code_structure(content)
            
            # Registrar el archivo como nodo
            memory.graph.add_node(file, type="file")
            
            # Registrar imports como relaciones
            for imp in structure["imports"]:
                # Aquí simplificaremos: si el import menciona otro archivo del repo
                for target_file in files:
                    if target_file.replace(".py", "") in imp:
                        memory.add_relationship(file, target_file, "imports")
    
    memory.save_to_disk()
    return memory



if __name__ == "__main__":
    app()