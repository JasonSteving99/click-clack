from typing import cast
import asyncclick
import asyncio
from collections import Counter
import click
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
import functools
import io

from mcp.server.fastmcp import FastMCP
from click_clack.crawl import crawl_click_commands
from click_clack.utils.generate_help import generate_help


@dataclass(frozen=True)
class OptionData:
    opt_cli_name: str
    is_flag: bool


async def _click_command_wrapper(cmd: click.Command | asyncclick.Command, **kwargs) -> str:
    # In order to have Click handle necessary type conversions, we need to go through the
    # "front door" of calling the command's main method, and we can't just
    options = {
        opt.name: OptionData(opt_cli_name=opt.opts[0], is_flag=cast(click.Option, opt).is_flag)
        for opt in cmd.params
    }

    rendered_options = []
    for arg_name, value in kwargs.items():
        rendered_options.append(options[arg_name].opt_cli_name)
        if not options[arg_name].is_flag:
            rendered_options.append(value)

    async def async_cmd_handler(**kwargs) -> None:
        if isinstance(cmd, asyncclick.Command):
            await cmd.main(**kwargs)
        else:
            cmd.main(**kwargs)

    return await _capture_stdout_and_stderr(
        async_cmd_handler,
        args=rendered_options,
        standalone_mode=False,  # Don't auto-exit the interpreter on finish.
    )


async def _capture_stdout_and_stderr(func, *args, **kwargs) -> str:
    # Create a StringIO object to capture output
    f = io.StringIO()

    # Redirect stdout & stderr to our StringIO object
    with redirect_stdout(f), redirect_stderr(f):
        await func(*args, **kwargs)

    # Get the captured output as a string
    output = f.getvalue()

    return output


def _get_cmd_tool_name_and_desc(
    _cmd: click.Command | asyncclick.Command, _location: str, _cmd_counts: Counter
) -> tuple[str | None, str]:
    # It's possible that the same command name is used repeatedly in the codebase (note that this
    # "name" is actually just the name of the function decorated with @click.command() so honestly
    # it's not that surprising if it'll be duplicated). If it is, we need to distinguish them in the
    # ui somehow.
    desc = asyncio.run(generate_help(_cmd))
    if _cmd_counts[_cmd.name] > 1:
        return f"{_cmd.name}_{_location.__hash__()}", f"Command location: {_location}\n{desc}"
    return _cmd.name, desc


def generate_mcp_server(server_name: str, module_path: str, exclude_files: list[str]) -> FastMCP:
    # Create a FastMCP server to add discovered commands to.
    mcp = FastMCP(server_name)

    # Crawl all the click commands in the given dir.
    discovered_commands: list[tuple[click.Command, str]] = crawl_click_commands(
        module_path=module_path, exclude=exclude_files
    )
    command_name_counts = Counter([c[0].name for c in discovered_commands])

    # Add all the discovered commands to the FastMCP server.
    for cmd in discovered_commands:
        if fn := cmd[0].callback:
            # Wrap the function in stdout capturing - but make sure we don't lose the type signature
            # that FastMCP needs so it can tell the LLM what args to pass. The click-clack contract
            # with discovered click commands is we'll collect stdout and return it to the LLM.
            wrapped_fn = functools.wraps(fn)(functools.partial(_click_command_wrapper, cmd[0]))
            # Make sure that we come up with uniqe names for discovered commands with duplicate names.
            name, desc = _get_cmd_tool_name_and_desc(cmd[0], cmd[1], command_name_counts)
            mcp.add_tool(wrapped_fn, name=name, description=desc)

    return mcp
