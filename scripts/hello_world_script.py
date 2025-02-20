import click

@click.command()
def hello_world():
  click.echo("Hello, world!")

if __name__ == "__main__":
  hello_world()