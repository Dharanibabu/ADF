"""
    Module to generate project hierarchy.
    It contains the classes and functions required to generate the project hierarchy.
"""

import os
import glob
from re import sub
from adf.utils import USE_CASE_TEMPLATES_DIR, jinja_env


class Scaffold:
    """
        Class to generate base project hierarchy.

        This class is used to generate use case specific project hierarchy using pre-defined project hierarchy under
        `bundle` directory.

        Attributes:
            project_root: contains the path of the project if specified in the `project_name` argument, otherwise it
                            assumes the path from which it has been called
            project_name: contains only the name of the project. This name will be converted to camel case by default.

    """

    def __init__(self, project_name: str):
        """
            Usual Initializer

        :param project_name: Name of the project. Name may contain path to which project has to be generated.
        """
        project_props = self._camel_case(project_name)
        self.project_root = os.path.join(os.path.abspath(project_props[0]), '')
        self.project_name = project_props[1]

    @staticmethod
    def _camel_case(project_name: str) -> tuple:
        """
            Method to generate camel cased project name.

        :param project_name: Name of the project. It may or may not include project path
        :return: Camel cased project name
        """
        name = os.path.split(project_name)[-1]
        camel_cased_name = sub(r"(_|-)+", " ", name).title().replace(" ", "")
        return project_name.replace(name, camel_cased_name), camel_cased_name

    def _create_file_from_template(self, template_file_path: str, destination_file_path: str) -> None:
        """
            Method to generate files of any type using specified template file.

        :param template_file_path: Relative path to the template file
        :param destination_file_path: Absolute path of destination
        :return: None
        """
        # Identifies file with .jinja extension and format the name of the file
        if template_file_path.endswith('.jinja'):
            template_file = os.path.split(template_file_path)[-1]
            destination_file = template_file.replace('pfx_', self.project_name).replace('.jinja', '')
            destination_file_path = destination_file_path.replace(template_file, destination_file)

        template = jinja_env.get_template(template_file_path)
        file_content = template.render(jinja_model={'className': self.project_name})
        with open(destination_file_path, 'w') as file:
            file.write(file_content)
        print('Created {0}'.format(destination_file_path))

    def create_project_structure(self) -> None:
        """
            Method to generate directories and files from template.

        :return: None
        """
        for source in glob.iglob(USE_CASE_TEMPLATES_DIR + '/**/*', recursive=True):
            destination = source.replace(USE_CASE_TEMPLATES_DIR, self.project_root)
            if os.path.isdir(source):
                os.makedirs(destination)
                print('Created {0}'.format(destination))
            else:
                source_file_path = source.replace(USE_CASE_TEMPLATES_DIR, '').replace('\\', '/')
                self._create_file_from_template(source_file_path, destination)
