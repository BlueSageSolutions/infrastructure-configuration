import sys
from typing import List, Dict
from invoke import task
from src import Config
from src.ec2_client import Ec2Client, Ec2ClientResponse, Instance
from src.templater import Templater
from src.ssm_client import SsmClient, GetParametersResponse, NginxPortMapping


@task
def inventory_template(
    _,
    envs: str,
    client_code: str,
    client_account_aws_profile: str = "it-devops-bss",
):
    """
    Templates out ansible inventory yaml configuration file

    Args:
        envs: A comma delinatied list of environments. Cannot include spaces. Ex: dev,qa,uat,foo,bar
        client_code: client code corresponding to client infrasture you want to configure using ansible
        client_account_aws_profile: name of aws profile that points to aws client account 
    """
    config = Config.new(environments=envs, client_code=client_code)

    ec2_client: Ec2Client = Ec2Client.new(profile_name=client_account_aws_profile)
    ssm_client: SsmClient = SsmClient.new(profile_name=client_account_aws_profile)

    ec2_instances: List[Instance] = get_ec2_instances(ec2_client=ec2_client, config=config)
    nginx_port_mappings: List[NginxPortMapping] = get_nginx_port_mapping(ssm_client=ssm_client, config=config, instances=ec2_instances)

    clients = ["allcu", "mam", "trcu", "tib", "ctcb"] if config.is_bluedlp() else [f"{config.get_client_code()}"]
    
    for client in clients:

        instances = [i for i in ec2_instances if i.client.startswith(f"{client}")]

        template_data = {
            "environments": config.get_environments(),
            "client_code": client,
            "instances": instances,
            "client_account_aws_profile": client_account_aws_profile,
            "ssh_private_key_file_path": config.get_ssh_key_filepath(),
            "nginx_port_mappings": nginx_port_mappings,
            "is_bluedlp": config.is_bluedlp()
        }

        validate_template_vars(template_data)
                
        try:
            templater: Templater = Templater.new(config=config)
            rendered_template = templater.render(template_data=template_data)
            templater.write_template(
                rendered_template=rendered_template, client_code=client
            )
        except Exception as e:
            print(f"Error rendering template: {e}")
            print(f"Instances:\n")
            for i in instances:
                print(f"{i}\n")
            print("----------------------------")
            print(f"Nginx port mappings:\n")
            for p in nginx_port_mappings:
                print(f"{p}\n")


def get_ec2_instances(ec2_client: Ec2Client, config: Config) -> List[Instance]:
    ec2_response: Ec2ClientResponse = ec2_client.get_instances_by_environment(
        environments=config.get_environments()
    )
    instances: List[Instance] = ec2_response.get_instances()

    return instances

def get_nginx_port_mapping(ssm_client: SsmClient, config: Config, instances: List[Instance]) -> List[NginxPortMapping]:
    client_code = config.get_client_code()

    parameter_names: List[str] = []

    for instance in instances:
        server = instance.get_name().split(f"{instance.env}-")[-1].split("-")[0]
        env = instance.env

        if client_code == "bluedlp":
            sub_client = instance.get_name().split(f"{instance.env}-")[0].split("-")[0]
            parameter_names.append(NginxPortMapping.get_parameter_path(client_code=sub_client, env=env, server=server))
        else:
            if client_code == "springeq":
                parameter_names.append(NginxPortMapping.get_parameter_path(client_code="springeqfirst", env=env, server=server))
            parameter_names.append(NginxPortMapping.get_parameter_path(client_code=client_code, env=env, server=server))

    ssm_response: GetParametersResponse = ssm_client.get_parameters_by_name(
        names=parameter_names
    )

    nginx_port_mappings: List[NginxPortMapping] = [NginxPortMapping(**parameter.model_dump()) for parameter in ssm_response.Parameters]

    return nginx_port_mappings

def validate_template_vars(vars: Dict):

    if len(vars.get("instances")) == 0:
        print("List of EC2 instances is empty")
        sys.exit()
    elif len(vars.get("nginx_port_mappings")) == 0:
        print("List of nginx port mappings is empty")
        sys.exit()