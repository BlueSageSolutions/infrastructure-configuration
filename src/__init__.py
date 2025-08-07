from __future__ import annotations
from typing import List

class Config:
    
    def __init__(self, environments: List[str], output_directory: str, client_code: str):
        self._environments = environments
        self._output_directory = output_directory
        self._client_code = client_code

    def get_environments(self) -> List[str]:
        return self._environments
    
    def get_client_code(self) -> str:
        return self._client_code
    
    def get_output_directory(self) -> str:
        return self._output_directory
    
    def get_stage(self) -> str:
        return "prod" if self.is_prod() else "lower"
    
    def get_ssh_key_filepath(self) -> str:
        return f"../../../keys/{'bluedlp' if self.is_bluedlp() else self._client_code}_{self.get_stage()}.pem"

    def is_prod(self) -> bool:
        return True if "prod" in self._environments else False
    
    def is_bluedlp(self) -> bool:
        return True if self.get_client_code() == "bluedlp" else False

    @staticmethod
    def new(environments: str, client_code: str) -> Config:
        output_directory = "inventory"

        environments = [e for e in environments.strip().split(",") if e != ""]

        return Config(environments=environments, output_directory=output_directory, client_code=client_code)
        

