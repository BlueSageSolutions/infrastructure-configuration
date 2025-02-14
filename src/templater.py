from typing import Dict
from jinja2 import Environment, FileSystemLoader, Template
from src import Config

class Templater:
    def __init__(self, template: Template, config: Config):
        self.template: Template = template
        self.config: Config = config

    def render(self, template_data: Dict[str, str]) -> str:
        rendered_template = self.template.render(template_data)
        return rendered_template
    
    def write_template(self, rendered_template: str, client_code):

        output_file_path = self.get_output_file_path(client_code=client_code)
        
        with open(output_file_path, "w") as f:
            f.write(rendered_template)
    
    def get_output_file_path(self, client_code: str):

        stage = self.config.get_stage()
        output_dir = self.config.get_output_directory()

        return f"{output_dir}/{stage}/01-{client_code}.yml"

    @staticmethod
    def new(config: Config):
        stage = config.get_stage()
        template_path = f"templates/inventory/{stage}.yml.jinja"
        environment = Environment(loader=FileSystemLoader('./'))
        template: Template = environment.get_template(template_path)

        return Templater(template=template, config=config)

