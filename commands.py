import typer
from rich.console import Console
from tools.reader import CodeReader
from tools.parser import get_code_structure
from memory.graph_manager import MemoryManager

console = Console()

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