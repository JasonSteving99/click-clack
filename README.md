# Auto Generated Minimalist UI For All of Your Python Scripts

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
![Scripts UI](https://raw.githubusercontent.com/JasonSteving99/python-script-ui/refs/heads/main/images/minimalist_ui_example.png)

...simply enter any values, and click `Run Command!`:
![Run Command](https://raw.githubusercontent.com/JasonSteving99/python-script-ui/refs/heads/main/images/minimalist_ui_example_run.png)

## How It Works

This project crawls all `.py` files at and below the directory where the `click-clack` command is run. It then automatically traverses the Python AST looking for the `@click.command()` decorator, and imports the decorated commands and generates a minimalist UI for them.

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