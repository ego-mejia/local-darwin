# memory/graph_manager.py
import networkx as nx
import sqlite3
import pickle

class MemoryManager:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self.graph = nx.DiGraph()
        self._init_db()

    def _init_db(self):
        """Crea la tabla para persistir el grafo."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS graph_store (id INTEGER PRIMARY KEY, data BLOB)")

    def add_relationship(self, source: str, target: str, rel_type: str):
        """Añade una conexión entre dos elementos de código."""
        self.graph.add_edge(source, target, relation=rel_type)

    def get_related_nodes(self, node: str):
        """Encuentra qué archivos están conectados a uno dado."""
        if node in self.graph:
            # Vecinos directos (quién depende de quién)
            return list(self.graph.neighbors(node)) + list(self.graph.predecessors(node))
        return []

    def save_to_disk(self):
        """Guarda el objeto del grafo en SQLite."""
        data = pickle.dumps(self.graph)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM graph_store")
            conn.execute("INSERT INTO graph_store (data) VALUES (?)", (data,))

    def load_from_disk(self):
        """Carga el grafo guardado."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT data FROM graph_store")
                row = cursor.fetchone()
                if row:
                    self.graph = pickle.loads(row[0])
        except Exception:
            self.graph = nx.DiGraph()