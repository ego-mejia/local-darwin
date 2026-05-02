import os
from typing import List

class CodeReader:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path
        # Carpetas que ignoramos siempre
        self.ignore_dirs = {".git", "__pycache__", "node_modules", "venv", ".uv"}

    def list_files(self) -> List[str]:
        """Lista todos los archivos relevantes en el proyecto."""
        files_list = []
        for root, dirs, files in os.walk(self.base_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            for file in files:
                if file.endswith((".py", ".js", ".ts", ".md")): # Extensiones soportadas
                    files_list.append(os.path.relpath(os.path.join(root, file), self.base_path))
        return files_list

    def read_file(self, file_path: str) -> str:
        """Lee el contenido de un archivo."""
        with open(os.path.join(self.base_path, file_path), "r", encoding="utf-8") as f:
            return f.read()