from __future__ import annotations

import click
import os
import sys

from marimo._server.start import start
from marimo._server.file_router import AppFileRouter
from marimo._server.tokens import AuthToken
from marimo._utils.marimo_path import MarimoPath
from marimo._cli.parse_args import parse_args
from marimo._config.settings import GLOBAL_SETTINGS
from marimo._server.model import SessionMode

from click_clack import ClickClack
from click_clack.mcp import generate_mcp_server


@click.command()
@click.option(
    "--mcp",
    is_flag=True,
    default=False,
    help="Run click_clack as an MCP server. Expose all crawled commands to an LLM via the MCP protocol.",
)
@click.option(
    "--module-path",
    default=None,
    type=click.Path(),
    help="The path to be crawled for commands.",
)
def click_clack(mcp: bool, module_path) -> None:
    """Runs the click-clack Marimo app."""
    if module_path:
        # We'll just move to the given module path so that relative imports work correctly when we
        # crawl the files for commands.
        os.chdir(module_path)

    # Ensure that the user is able to access their own scripts relative to the directory that they
    # ran click-clack from.
    sys.path.insert(0, os.getcwd())

    if mcp:
        mcp_server = generate_mcp_server("click_clack", module_path=os.getcwd(), exclude_files=[])
        mcp_server.run("stdio")
    else:
        # Lifted from marimo/_cli/cli.py::run - at some point may need to add the configurability
        # found in the original.
        start(
            file_router=AppFileRouter.from_filename(MarimoPath(ClickClack.__file__)),
            development_mode=GLOBAL_SETTINGS.DEVELOPMENT_MODE,
            quiet=GLOBAL_SETTINGS.QUIET,
            host="127.0.0.1",
            port=None,
            proxy=None,
            headless=False,
            mode=SessionMode.RUN,
            include_code=False,
            ttl_seconds=120,
            watch=False,
            base_url="",
            allow_origins=(),
            cli_args=parse_args(("run", ClickClack.__file__)),
            auth_token=AuthToken(""),
            redirect_console_to_browser=False,
        )


if __name__ == "__main__":
    click_clack()
