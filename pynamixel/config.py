import json
import yaml
import os
from typing import  List, Dict, Tuple, Union
from pathlib import Path
from abc import ABC, abstractmethod
from builtins import FileNotFoundError, ValueError


class ConfigManager:
    def __init__(self, file_path: List[Union[str, Path]]=None, config_loader_: 'ConfigLoaderBase' = None):
        self.__config_data = {}
        self.is_config_initialized = False
        self.__config_file_type = None
        self.__config_file_path = file_path
        self.__config_loader = config_loader_
    
    def __load_config_file(self):
        config_data = self.config_loader.load_config(self.__config_file_path)
        if not isinstance(config_data, dict):
            raise ValueError("Loaded config data must be a dictionary")
        if not config_data:
            raise ValueError("Loaded config data is empty")
        
        self.__config_data = config_data
        self.is_config_initialized = True

    def load_config_from_file(self, loader:'ConfigLoaderBase'=None, file_path=None):
        self.config_file_path = file_path or self.__config_file_path
        self.config_loader = loader or self.__config_loader   
        self.__load_config_file()
    
    def save_config_to_file(self, file_path=None):
        self.config_file_path = file_path or self.__config_file_path
        assert self.config_loader is not None, "The config loader must be set."
        
        self.config_loader.save_config(self.config_data, self.config_file_path)
    
    @property
    def config_loader(self):
        return self.__config_loader
    
    @config_loader.setter
    def config_loader(self, loader: 'ConfigLoaderBase'):
        if loader is None:
            raise ValueError("Loader must contain a value")
        if not isinstance(loader, ConfigLoaderBase):
            raise ValueError("Loader must be an instance of < class ConfigLoaderBase > or its subclasses")
        self.__config_file_type = loader.__class__.__name__.lower().replace('configloader', '')
        self.__config_loader = loader   
        
    @property
    def config_data(self):
        return self.__config_data
    
    @property
    def config_file_path(self):
        return self.__config_file_path
    
    @config_file_path.setter
    def config_file_path(self, file_path: Union[str, Path]):
        if file_path is None:
            raise ValueError("File path must contain a value")
        if not isinstance(file_path, (str, Path)):
            raise ValueError("File path must be str or path")
        self.__config_file_path = file_path
        
    def __setattr__(self, name, value): 
        if self.__dict__.get("__config") is None or name  not in self.__config_data:
            super().__setattr__(name, value)
        else:
            self.__config_data[name] = value
    
    def __getattr__(self, name):    
        if name in self.__config_data:
            return self.__config_data[name]
        
        return super().__getattr__(name)
    
    def __getitem__(self, key):
        return self.__config_data[key]
    
    def __setitem__(self, key, value):
        self.__config_data[key] = value
    
    def __contains__(self, key):
        return key in self.__config_data
    
    def __iter__(self):
        return iter(self.__config_data.items())
    
    def __len__(self):
        return len(self.__config_data)
    
    def to_dict(self):
        return self.__config_data


class ConfigLoaderBase(ABC):
    
    def __init__(self):
        self.__file_path = None
    
    @abstractmethod
    def load_config(self, file_path: List[Union[str, Path]]=None):
        pass
    
    @abstractmethod
    def save_config(self, config: Dict[str, Union[str, int, float]], file_path: Union[str, Path]) -> bool:
        pass

    def check_path(self, file_path: Union[str, Path]) -> Union[str, Path]: 
        if file_path is None:
            assert self.__file_path is not None, "File path must be set"
            return self.__file_path
            
        else:
            assert isinstance(file_path, (str, Path)), "File path must be str or path"
            return file_path
            
            
class YamlConfigLoader(ConfigLoaderBase):

    def load_config(self, file_path: List[Union[str, Path]]=None):
        self.__file_path = self.check_path(file_path)
        if not os.path.exists(self.__file_path):
            raise FileNotFoundError(f"File not found: {self.__file_path}")

        with open(self.__file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    
    def save_config(self, config: Dict[str, Union[str, int, float]], file_path: Union[str, Path] =None) -> bool:
        _path = self.check_path(file_path)
        
        try:
            config = yaml.safe_load(config.strip()) if isinstance(config, str) else config
            with open(_path, 'w') as file:
                yaml.dump(config, file, default_flow_style=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False


class JsonConfigLoader(ConfigLoaderBase):

    def load_config(self, file_path: List[Union[str, Path]]=None):
        self.__file_path = self.check_path(file_path)
        if not os.path.exists(self.__file_path):
            raise FileNotFoundError(f"File not found: {self.__file_path}")

        with open(self.__file_path, 'r') as file:
            config = json.load(file)
        return config

    def save_config(self, config: Dict[str, Union[str, int, float]], file_path=None) -> bool:
        _path = self.check_path(file_path)
        
        try:
            config = json.loads(config.strip()) if isinstance(config, str) else config
            with open(_path, 'w') as file:
                json.dump(config, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

