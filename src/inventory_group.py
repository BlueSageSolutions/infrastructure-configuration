import yaml

from src import Config

def update_inventory_group(config: Config, client_code: str):

    stage = config.get_stage()
    environments = config.get_environments()
    output_dir = config.get_output_directory()
    
    for env in environments:
        file_path = f"./{output_dir}/{stage}/02-{env}.yml"
        update_yaml_file(file_path=file_path, parent_key=env, key=f"{client_code}_{env}")

        if not config.is_prod():
            file_path = f"./{output_dir}/lower/03-lower.yml"
            update_yaml_file(file_path=file_path, parent_key="lower", key=env)
    
def update_yaml_file(file_path: str, parent_key: str, key: str):
    
    with open(file_path, "r") as f:
        data = yaml.full_load(f)
        data[parent_key]["children"][key] = None

    with open(file_path, "w", encoding='utf-8') as f:
        yaml.dump(data, f)