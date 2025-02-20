# Auto Generated Minimalist UI For All of Your Python Scripts

For example, when run over the root of this git repo:

```bash
$ tree
.
├── Makefile
├── README.md
├── ScriptsUI.py
├── images
│   └── minimalist_ui_example.png
├── pyproject.toml
├── requirements.in
├── requirements.txt
├── scripts
│   ├── hello_world_script.py    # <-- This is a script that contains a @click.command()
│   └── test
│       └── sup.py               # <-- This is a script that contains a @click.command()
├── scripts-ui.code-workspace
├── tool-requirements.in
└── tool-requirements.txt

4 directories, 12 files
```

...and run the following commands:
```bash
$ source .venv/bin/activate
$ make install  # Or wtv pip/uv command you use to setup your virtualenv.
$ marimo run ScriptsUI.py
```

...you'll get a minimalist UI that looks like this:
![Scripts UI](https://raw.githubusercontent.com/JasonSteving99/python-script-ui/refs/heads/main/images/minimalist_ui_example.png)

## How It Works

This project crawls all `.py` files at and below the directory where the `marimo run ScriptsUI.py` command is run. It then automatically traverses the Python AST looking for the `@click.command()` decorator, and imports the decorated commands and generates a minimalist UI for them.

## Command Parameter Discovery

The UI will generate an input for each command parameter, and will forward the data from the input to the command.

### Supported Command Parameter Types

Currently this project only supports automatically discovering the following command parameter types:
- `str`
- ...literally everything else is a TODO...