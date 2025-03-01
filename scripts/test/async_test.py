import asyncclick as click
from asyncio import sleep


@click.command()
@click.option("--delay", default=1.0, help="Some arbitrary sleep delay in seconds.")
async def async_test(delay: float):
    click.echo(f"Gonna sleep {delay} seconds...")
    await sleep(delay)
    click.echo("Done!")
