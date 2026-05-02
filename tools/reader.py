import os
from typing import List

class CodeReader:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        # Elementos (archivos/carpetas) que ignoramos por defecto
        self.ignore_items = {".git", "__pycache__", "node_modules", "venv", ".venv"}
        
        # Cargar el archivo .darwinignore (buscamos en la raíz)
        ignore_file_path = os.path.join(self.base_path, ".darwinignore")
        if os.path.exists(ignore_file_path):
            with open(ignore_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ignore_items.add(line)

    def list_files(self) -> List[str]:
        """Lista todos los archivos relevantes en el proyecto."""
        files_list = []
        for root, dirs, files in os.walk(self.base_path):
            # Ignorar carpetas no deseadas
            dirs[:] = [d for d in dirs if d not in self.ignore_items]
            for file in files:
                if file in self.ignore_items:
                    continue
                if file.endswith((".py", ".js", ".ts", ".md")): # Extensiones soportadas
                    files_list.append(os.path.relpath(os.path.join(root, file), self.base_path))
        return files_list

    def read_file(self, file_path: str) -> str:
        """Lee el contenido de un archivo."""
        with open(os.path.join(self.base_path, file_path), "r", encoding="utf-8") as f:
            return f.read()