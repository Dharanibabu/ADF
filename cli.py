
import click
from adf.scaffold import Scaffold


@click.group()
def cli():
    pass


@cli.command()
@click.argument('project_name')
def scaffold(project_name):
    try:
        Scaffold(project_name).create_project_structure()
        print('Done!')
    except FileExistsError as fee:
        print('Project already exists!')
        exit(1)


if __name__ == '__main__':
    cli()
