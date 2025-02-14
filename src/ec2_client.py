from __future__ import annotations
from typing import Dict, List

from pydantic import BaseModel
from boto3 import Session


class Ec2Client:
    def __init__(self, client):
        self.client = client

    def get_instances_by_environment(self, environments: List[str]) -> Ec2ClientResponse:
        response: Dict[str, str] = self.client.describe_instances(
            Filters=[
                {
                    "Name": "tag:Env",
                    "Values": environments,
                },
                {
                    "Name": "instance-state-name",
                    "Values": ["running"]
                }
            ],
        )
        response = Ec2ClientResponse(**response)
        
        return response

    @staticmethod
    def new(profile_name: str) -> Ec2Client:
        session = Session(profile_name=profile_name)
        client = session.client('ec2')
        ec2_client = Ec2Client(client)
        return ec2_client


class Ec2ClientResponse(BaseModel):
    Reservations: List[Reservation]

    def get_instances(self) -> List[Instance]:
        instances = [r.get_instances() for r in self.Reservations]
        instances = [i for j in instances for i in j]
        return instances

class Reservation(BaseModel):
    Instances: List[Instance]

    def get_instances(self):
        return self.Instances

class Instance(BaseModel):
    PrivateIpAddress: str
    Tags: List[Dict[str, str]]

    def get_name(self) -> str:
        return self.__parse_tags("Name")
            
    def get_apps(self) -> List[str]:
        apps = self.__parse_tags("Apps").split(",")
        return apps
    
    @property
    def env(self) -> str:
        return self.__parse_tags("Env")
    
    def get_ip_address(self) -> str:
        return self.PrivateIpAddress

    def __parse_tags(self, key: str):
        for tag in self.Tags:
            if tag.get("Key") == key:
                return tag.get("Value")