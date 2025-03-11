# Auto Generated MCP Server & UI For All of Your Python Scripts

For example, when in a repo containing the following files:

```bash
$ tree
.
...
├── scripts
│   ├── hello_world_script.py    # <-- Script containing a @click.command()
│   ├── options_test.py          # <-- Script containing a @click.command()
│   ├── not_a_click_cmd.py
│   └── test
│       └── sup.py               # <-- Script containing a @click.command()
...
```

...and run the following commands:
```bash
$ source .venv/bin/activate
$ pip install click-clack  # Or wtv pip/uv command you use to setup your virtualenv.
$ click-clack

        Running ClickClack.py ⚡

        ➜  URL: http://localhost:2718
```

...you'll get a minimalist UI that looks like this:
![Scripts UI](https://raw.githubusercontent.com/JasonSteving99/click-clack/refs/heads/main/images/minimalist_ui_example.png)

...simply enter any values, and click `Run Command!`:
![Run Command](https://raw.githubusercontent.com/JasonSteving99/click-clack/refs/heads/main/images/minimalist_ui_example_run.png)

## Auto Generated MCP Server

If you'd like to make your click commands accessible to MCP Clients such as [Claude Desktop](https://claude.ai/download), simply add the following config to `claude_desktop_config.json` (see https://modelcontextprotocol.io/quickstart/user for more info):

```json
{
    "mcpServers": {
        "click_clack": {
            "command": "uv",
            "args": [
                "run",
                "--directory",
                "/path/to/directory/with/your/click/commands"
                "--",
                "click-clack",
                "--mcp",
                "--module-path",
                "/path/to/directory/with/your/click/commands"
            ]
        }
    }
}
```

Note that for this to work as documented above, you'll need to [install `uv`](https://docs.astral.sh/uv/getting-started/installation/) globally first and the `/path/to/directory/with/your/click/commands` directory must be a valid uv project (i.e. you ran `uv init` there and `uv add`ed the dependencies your commands need).

For example, in Claude Desktop once properly configured you'll be able to see the available tools provided by the `click-clack` MCP server.
![Claude Desktop Example](https://raw.githubusercontent.com/JasonSteving99/click-clack/refs/heads/main/images/claude_desktop_mcp_tools_example.png)

### Note on MCP Tool Outputs!

Click commands don't generally return values, so instead when running your commands as an MCP tool, Click Clack will **capture all stdout/stderr output that your command emits, and redirect that to the MCP client as your tool's reponse**. So, instead of returning your final tool response, use `print(response)` instead.

## How It Works

This project crawls all `.py` files at and below the directory where the `click-clack` command is run. It then automatically traverses the Python AST looking for the `@click.command()` decorator, and imports the decorated commands and generates a minimalist UI for them.

### Support for [click](https://pypi.org/project/click/) and [asyncclick](https://pypi.org/project/asyncclick/)
Whether you're writing basic `click` commands, or using `asyncclick` to write async commands, `click-clack` seamlessly supports your command by auto-detecting the command type.

### UI Generation via [Marimo](https://marimo.io)
[Marimo](https://marimo.io) fundamentally underpins this package by providing an extremely simple framework for generating interactive UIs in pure python.

### MCP Server Generation via [FastMCP](https://github.com/jlowin/fastmcp/tree/main)
MCP Server generation is entirely based on [FastMCP](https://github.com/jlowin/fastmcp/tree/main), which does almost all of the heavy lifting. Click Clack just performs auto-discovery and does a bit of clever wrapping of your Click commands to be able to pass them off to FastMCP as tools.

## Command Parameter Discovery

The UI will generate an input for each command parameter, and will forward the data from the input to the command.

### Supported Command Parameter Types

Currently this project only supports automatically discovering the following command parameter types:
- `str`
- `int`
- `float`
- `bool` (including `is_flag=True`)
- `click.Choice`
- `click.File` (via a file browser UI element: TODO - support stdout via click's magic `"-"` file arg support)
- `click.Path`
- `click.DateTime`
- `click.IntRange`
- `click.FloatRange`
- ...literally everything else is a TODO...
