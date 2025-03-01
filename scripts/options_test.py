import click


@click.command()
@click.option("--count", type=click.INT, default=1, help="Number of times to greet.")
@click.option("--price", type=click.FLOAT, help="The price.")
@click.option("--verbose", is_flag=True, default=False, help="Enable verbose output.")
@click.option(
    "--color", type=click.Choice(["red", "green", "blue"]), default="blue", help="Choose a color."
)
@click.option("--date", type=click.DateTime(formats=("%Y-%m-%d", "%d/%m/%Y")), help="Some date.")
@click.option("--some-file", type=click.File(), help="Some file to pass to this cmd.")
@click.option("--some-path", type=click.Path(), help="Some path to pass to this cmd.")
@click.option("--int-val", type=click.IntRange(min=1, max=10), help="Some arbitrary integer value.")
@click.option(
    "--float-val",
    type=click.FloatRange(min=1.5, max=10.5),
    help="Some arbitrary float value.",
)
def options_test(count, price, verbose, color, date, some_file, some_path, int_val, float_val):
    """A script to test various option types."""
    for _ in range(count):
        greeting = f"Hello, with color {color}"
        if verbose:
            greeting += " (verbose mode)"
        if price:
            greeting += f", price is {price}"
        if date or some_file or some_path:
            greeting += " -- ("
            if date:
                greeting += f" Date: {date} "
            if some_file:
                greeting += f" File: {some_file.name} "
            if some_path:
                greeting += f" Path: {some_path} "
            greeting += ")"
        click.echo(greeting + "!")
        if int_val:
            click.echo(f"int_val: {int_val}")
        if float_val:
            click.echo(f"float_val: {float_val}")


if __name__ == "__main__":
    options_test()
