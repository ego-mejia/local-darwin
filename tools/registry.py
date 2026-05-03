# tools/registry.py
import os

def read_file(path: str):
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)
    return f"Archivo {path} escrito con éxito."

def list_dir(path: str = "."):
    return os.listdir(path)

# Diccionario de herramientas disponibles
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_dir": list_dir
}

# tools/registry.py
import os
import subprocess
from rich.prompt import Confirm

def execute_command(command: str):
    """Ejecuta un comando pero pide permiso al usuario primero."""
    if Confirm.ask(f"[bold yellow]⚠️ El agente quiere ejecutar:[/bold yellow] `{command}`. ¿Permitir?"):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            return result
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar: {e.output}"
    return "Acción cancelada por el usuario."

# Actualiza el diccionario
AVAILABLE_TOOLS = {
    "read_file": read_file, # La que ya tenías
    "write_file": write_file, # La que ya tenías
    "execute_command": execute_command,
    "list_dir": list_dir
}