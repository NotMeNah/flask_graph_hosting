from abc import ABC,abstractmethod
from werkzeug.datastructures import FileStorage

class ImageStorage(ABC):
    @abstractmethod
    def save_image(self,file:FileStorage,filename:str)->str:
        pass
    @abstractmethod
    def get_file_identifier(self,graph_id:str)->str:
        pass
    @abstractmethod
    def get_image_url(self,file_identifier:str)->str:
        pass