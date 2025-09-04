from datetime import datetime
from typing import List, Dict

class Noticia:
    def __init__(
        self,
        titulo: str,
        url: str,
        id:str,
        fuente: str,
        autores: List[str],
        fecha_publicacion: datetime,
        entradilla: str,
        cuerpo: str,
        etiquetas: List[str] = None,
        entidades: Dict[str, List[str]] = None,
    ):
        self.titulo = titulo
        self.url = url
        self.id = id
        self.fuente = fuente
        self.autores = autores
        self.fecha_publicacion = fecha_publicacion
        self.entradilla = entradilla
        self.cuerpo = cuerpo
        self.etiquetas = etiquetas or []
        self.entidades = entidades or {}
    
    def to_dict(self) -> Dict:
        
        return {
            "titulo": self.titulo,
            "url": self.url,
            "fuente": self.fuente,
            "autores": self.autores,
            "fecha_publicacion": self.fecha_publicacion,
            "entradilla": self.entradilla,
            "cuerpo": self.cuerpo,
            "etiquetas": self.etiquetas,
            "entidades": self.entidades,
        }
    
    def __repr__(self) -> str:
        return f"----- Noticia '{self.titulo}', ({self.fuente}) -----"
