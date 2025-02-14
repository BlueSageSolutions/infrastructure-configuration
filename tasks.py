from typing import List
from invoke import task
from src import Config
from src.ec2_client import Ec2Client, Ec2ClientResponse, Instance
from src.ssm_client import SsmClient, GetParametersResponse, GetResourceTagsResponse, RdsCreds, NginxPortMapping
from src.templater import Templater
from src.inventory_group import update_inventory_group


@task
def inventory_template(
    _,
    envs: str,
    client_code: str,
    client_account_aws_profile: str = "it-devops-bss",
    bss_devops_account_aws_profile: str = "it-devops-bss-devops",
    ssh_private_key_file_path: str = "../BlueSage-Terraform/bss-terraform-infrastructure/bss-lower.pem",
):
    """
    Templates out ansible inventory yaml configuration file

    Args:
        envs: A comma delinatied list of environments. Cannot include spaces. Ex: dev,qa,uat,foo,bar
        client_code: client code corresponding to client infrasture you want to configure using ansible
        client_account_aws_profile: name of aws profile that points to aws client account 
        bss_devops_account_aws_profile: name of aws profile that points to aws bss-devops account 
        ssh_private_key_file_path: file path to .pem keys which can be used to ssh into the host ec2 instances
    """
    config = Config.new(environments=envs, client_code=client_code)

    ec2_client: Ec2Client = Ec2Client.new(profile_name=client_account_aws_profile)
    ssm_client: SsmClient = SsmClient.new(profile_name=bss_devops_account_aws_profile)

    instances: List[Instance] = get_ec2_instances(ec2_client=ec2_client, config=config)

    rds_creds: List[RdsCreds] = get_rds_creds(ssm_client=ssm_client, config=config)
    ssm_client.update_client_profile(profile_name=client_account_aws_profile)
    nginx_port_mappings: List[NginxPortMapping] = get_nginx_port_mapping(ssm_client=ssm_client, config=config, instances=instances)

    template_data = {
        "environments": config.get_environments(),
        "client_code": client_code,
        "instances": instances,
        "rds_creds": rds_creds,
        "nginx_port_mappings": nginx_port_mappings,
        "client_account_aws_profile": client_account_aws_profile,
        "ssh_private_key_file_path": ssh_private_key_file_path,
    }

    templater: Templater = Templater.new(config=config)
    rendered_template = templater.render(template_data=template_data)
    templater.write_template(
        rendered_template=rendered_template, client_code=client_code
    )

    update_inventory_group(config=config, client_code=client_code)

def get_ec2_instances(ec2_client: Ec2Client, config: Config) -> List[Instance]:
    ec2_response: Ec2ClientResponse = ec2_client.get_instances_by_environment(
        environments=config.get_environments()
    )
    instances: List[Instance] = ec2_response.get_instances()

    return instances

def get_rds_creds(ssm_client: SsmClient, config: Config) -> List[RdsCreds]:
    parameter_names = [
        RdsCreds.get_parameter_path(client_code=config.get_client_code(), env=env)
        for env in config.get_environments()
    ]
    ssm_response: GetParametersResponse = ssm_client.get_parameters_by_name(
        names=parameter_names
    )
    rds_creds: List[RdsCreds] = [
        RdsCreds.model_validate_json(parameter.get_value())
        for parameter in ssm_response.Parameters
    ]

    return rds_creds

def get_nginx_port_mapping(ssm_client: SsmClient, config: Config, instances: List[Instance]) -> List[NginxPortMapping]:
    client_code = config.get_client_code()

    parameter_names: List[str] = []

    for instance in instances:
        server_name = instance.get_name().split(f"{instance.env}-")[-1].split("-")[0]
        env = instance.env
        parameter_names.append(NginxPortMapping.get_parameter_path(client_code=client_code, env=env, server_name=server_name))

    ssm_response: GetParametersResponse = ssm_client.get_parameters_by_name(
        names=parameter_names
    )

    nginx_port_mappings: List[NginxPortMapping] = []
    for parameter in ssm_response.Parameters:
        port_mapping = NginxPortMapping(**parameter.model_dump())

        resource_tags: GetResourceTagsResponse = ssm_client.get_resource_tags(resource_id=parameter.get_name())
        port_mapping.update_tags(resource_tags)

        nginx_port_mappings.append(port_mapping)

    return nginx_port_mappings
