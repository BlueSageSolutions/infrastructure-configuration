from __future__ import annotations
from typing import List

class Config:
    
    def __init__(self, is_prod: bool, environments: List[str], out_put_directory: str, client_code: str):
        self._is_prod = is_prod
        self._environments = environments
        self._out_put_directory = out_put_directory
        self._client_code = client_code

    def get_environments(self) -> List[str]:
        return self._environments
    
    def get_client_code(self) -> str:
        return self._client_code
    
    def get_output_directory(self) -> str:
        return self._out_put_directory
    
    def get_stage(self) -> str:
        return "prod" if self.is_prod() else "lower"

    def is_prod(self) -> bool:
        return self._is_prod

    @staticmethod
    def new(environments: str, client_code: str) -> Config:
        is_prod = False
        out_put_directory = "inventory"

        environments = [e for e in environments.strip().split(",") if e != ""]

        if "prod" in environments:
            is_prod = True

        return Config(is_prod=is_prod, environments=environments, out_put_directory=out_put_directory, client_code=client_code)
        

