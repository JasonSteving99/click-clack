import asyncclick as click
from asyncio import sleep


@click.command()
@click.option("--delay", required=True, default=1.0, help="Some arbitrary sleep delay in seconds.")
@click.option("--some-required-opt-with-no-default", required=True)
async def async_test(delay: float, some_required_opt_with_no_default: str):
    click.echo(f"Gonna sleep {delay} seconds...")
    await sleep(delay)
    click.echo("Done!")
