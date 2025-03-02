"""If we have two commands whose functions are named identically, they need to be distinguished."""

import click


@click.command()
@click.option("--alt-greeting", help="Alternative greeting instead of 'sup'.")
@click.option("--name", default="bruh", help="The name of the person to greet.")
def sup(name: str, alt_greeting: str):
    greeting = "Sup"
    if alt_greeting:
        greeting = alt_greeting
    click.echo(f"{greeting}, {name}!")


if __name__ == "__main__":
    sup()
