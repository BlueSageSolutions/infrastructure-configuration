import sys
from typing import List, Dict
from invoke import task
from src import Config
from src.ec2_client import Ec2Client, Ec2ClientResponse, Instance
from src.templater import Templater
from src.inventory_group import update_inventory_group


@task
def inventory_template(
    _,
    envs: str,
    client_code: str,
    client_account_aws_profile: str = "it-devops-bss",
    bss_devops_account_aws_profile: str = "it-devops-bss-devops",
):
    """
    Templates out ansible inventory yaml configuration file

    Args:
        envs: A comma delinatied list of environments. Cannot include spaces. Ex: dev,qa,uat,foo,bar
        client_code: client code corresponding to client infrasture you want to configure using ansible
        client_account_aws_profile: name of aws profile that points to aws client account 
        bss_devops_account_aws_profile: name of aws profile that points to aws bss-devops account 
    """
    config = Config.new(environments=envs, client_code=client_code)

    ec2_client: Ec2Client = Ec2Client.new(profile_name=client_account_aws_profile)

    instances: List[Instance] = get_ec2_instances(ec2_client=ec2_client, config=config)

    template_data = {
        "environments": config.get_environments(),
        "client_code": client_code,
        "instances": instances,
        "client_account_aws_profile": client_account_aws_profile,
        "ssh_private_key_file_path": config.get_ssh_key_filepath(),
    }

    validate_template_vars(template_data)
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

def validate_template_vars(vars: Dict):

    if len(vars.get("instances")) == 0:
        print("List of EC2 instances is empty")
        sys.exit()
