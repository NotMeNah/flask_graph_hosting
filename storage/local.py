import os
from pathlib import Path
from werkzeug.datastructures import FileStorage
from .base import ImageStorage
from common.profile import Profile

class LocalStorage(ImageStorage):
    upload_dir:Path
    def __init__(self):
        self.upload_dir=Profile.get_graph_path()
        self.upload_dir.mkdir(parents=True,exist_ok=True)

    def save_image(self, file: FileStorage, filename: str) -> str:
        save_path = self.upload_dir / filename
        file.save(save_path)
        return f"data/graph/{filename}"

    def get_file_identifier(self,graph_id:str)->str | None:
        from models.graph import Graph
        graph=Graph.query.filter_by(graph_uuid=graph_id).first()
        if not graph or graph.storage_type !="local":
            return None
        return graph.file_identifier


    def get_image_url(self,file_identifier:str)->str:
        filename=os.path.basename(file_identifier)
        return f"http://127.0.0.1:5000/graph/{filename}"

