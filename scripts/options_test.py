import click


@click.command()
@click.option("--count", type=click.INT, default=1, help="Number of times to greet.")
@click.option("--price", type=click.FLOAT, help="The price.")
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output.")
@click.option(
    "--color", type=click.Choice(["red", "green", "blue"]), default="blue", help="Choose a color."
)
def options_test(count, price, verbose, color):
    """A script to test various option types."""
    for _ in range(count):
        greeting = f"Hello, with color {color}"
        if verbose:
            greeting += " (verbose mode)"
        if price:
            greeting += f", price is {price}"
        click.echo(greeting + "!")


if __name__ == "__main__":
    options_test()
