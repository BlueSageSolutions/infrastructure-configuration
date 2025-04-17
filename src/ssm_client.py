from __future__ import annotations
from typing import Dict, List

from pydantic import BaseModel
from boto3 import Session
import json


class SsmClient:

    def __init__(self, ssm_client):
        self.ssm_client = ssm_client

    def get_parameters_by_name(self, names: List[str]) -> GetParametersResponse:
        result: Dict[str, str] = {"Parameters": []}

        for pos in range(0, len(names), 10):
            name_sublist: List[str] = names[pos : pos + 10]
            response: Dict[str, str] = self.ssm_client.get_parameters(
                Names=name_sublist,
                WithDecryption=True,
            )
            result["Parameters"] += response["Parameters"]

        return GetParametersResponse(**result)

    def update_client_profile(self, profile_name: str):
        session = Session(profile_name=profile_name)
        ssm_client = session.client("ssm")
        self.ssm_client = ssm_client

    @staticmethod
    def new(profile_name: str) -> SsmClient:
        session = Session(profile_name=profile_name)
        ssm_client = session.client("ssm")

        return SsmClient(ssm_client)


class GetParametersResponse(BaseModel):
    Parameters: List[Parameter]


class Parameter(BaseModel):
    Name: str
    Value: str

    def get_value(self) -> str:
        return self.Value

    def get_name(self) -> str:
        return self.Name


class RdsCreds(BaseModel):
    hostname: str
    password: str
    username: str

    def get_hostname(self) -> str:
        return self.hostname

    def get_password(self) -> str:
        return self.password

    @property
    def env(self) -> str:
        return self.username.split("_")[-1]

    @staticmethod
    def get_parameter_path(client_code: str, env: str):
        return f"/secrets/{client_code}/{env}/database/application-user"


class GetResourceTagsResponse(BaseModel):
    TagList: List[Dict[str, str]]


class NginxPortMapping(BaseModel):
    Name: str
    Value: str
    _tags: List[Dict[str, str]]
    _env: str

    def update_tags(self, tags: GetResourceTagsResponse):
        self._tags = tags.TagList

    def mappings(self) -> Dict[int, List[str]]:
        mappings: Dict[int, List[str]] = {}
        values: Dict[str, int] = json.loads(self.Value)

        for app, port in values.items():
            if mappings.get(port):
                mappings[port].append(app)
            else:
                mappings[port] = [app]

        return mappings

    @property
    def app_name(self) -> str:
        return self.Name.split("/")[-1].split("-")[0]

    @staticmethod
    def get_parameter_path(client_code: str, env: str, app: str):
        return f"/secrets/{client_code}/{env}/nginx/{app}-ports"
