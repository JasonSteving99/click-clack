from __future__ import annotations

import os
import sys

from marimo._server.start import start
from marimo._server.file_router import AppFileRouter
from marimo._server.tokens import AuthToken
from marimo._utils.marimo_path import MarimoPath
from marimo._cli.parse_args import parse_args
from marimo._config.settings import GLOBAL_SETTINGS
from marimo._server.model import SessionMode

from src import ClickClack


def click_clack() -> None:
    """Runs the click-clack Marimo app."""

    # Ensure that the user is able to access their own scripts relative to the directory that they
    # ran click-clack from.
    sys.path.insert(0, os.getcwd())

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
