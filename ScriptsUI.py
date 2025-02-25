import marimo

__generated_with = "0.11.6"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from importlib import import_module
    import inspect
    import ast
    import os

    def find_decorated_objects(module_path, decorator_name, exclude):
        """
        Finds all classes and functions decorated with a specific decorator
        within a module or package.

        Args:
            module_path: The path to the module or package (directory).
            decorator_name: The name of the decorator (string).

        Returns:
            A list of tuples, where each tuple contains:
                - The object (class or function)
                - The module path where it's defined
        """

        decorated_objects = []

        def _find_in_ast(node, current_module_path):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                for decorator in node.decorator_list:
                    if (
                        (
                            hasattr(decorator, "func") and isinstance(decorator.func, ast.Attribute)
                        )  # @click.command()
                        and decorator.func.attr == decorator_name
                    ):
                        try:  # Handle potential import errors
                            imported_module = import_module(
                                current_module_path.replace("/", ".")[:-3]
                            )
                            decorated_objects.append(
                                (
                                    imported_module.__dict__[func_name],
                                    current_module_path,
                                )
                            )
                        except NameError:
                            # Likely a class/function defined in another module
                            pass  # Or handle differently if needed
                        break  # Found the decorator, no need to check others

            # FOR NOW I ONLY WANT TOP-LEVEL FUNCS
            # for child_node in ast.iter_child_nodes(node):
            #     _find_in_ast(child_node, current_module_path)

        def _process_module(path):
            with open(path, "r") as f:
                tree = ast.parse(f.read())
                for top_level_node in tree.body:
                    _find_in_ast(top_level_node, path)

        if os.path.isdir(module_path):  # Handle packages (directories)
            for root, _, files in os.walk(module_path):
                # We're traversing all dirs below the given module_path, so we need to check if it's a hidden dir, and avoid it if so.
                root = root[len(os.path.commonpath([module_path, root])) + 1 :]
                if root.startswith("."):
                    continue  # Skip this hidden dir.
                for file in files:
                    if file.endswith(".py"):
                        full_path = os.path.join(root, file)
                        if full_path in exclude:
                            continue
                        _process_module(full_path)
        else:
            raise ValueError("Invalid module path. Must be a directory.")

        return decorated_objects

    return ast, find_decorated_objects, import_module, inspect, os


@app.cell
def _(Optional, mo, os):
    DECORATOR_NAME_TEXT_AREA_FORM_FIELD = "decorator_name_text_area"
    EXCLUDE_FILE_BROWSER_FORM_FIELD = "exclude_file_browser"

    def _form_validator(form_json: dict[str, object]) -> Optional[str]:
        if not form_json[DECORATOR_NAME_TEXT_AREA_FORM_FIELD]:
            return "Decorator name is required!"

    form = (
        mo.md(f"""
    {{{DECORATOR_NAME_TEXT_AREA_FORM_FIELD}}}

    {{{EXCLUDE_FILE_BROWSER_FORM_FIELD}}}
    """)
        .batch(
            **{
                DECORATOR_NAME_TEXT_AREA_FORM_FIELD: mo.ui.text(
                    value="command", label="Decorator Name", full_width=True
                ),
                EXCLUDE_FILE_BROWSER_FORM_FIELD: mo.ui.file_browser(
                    label="Pick files to exclude",
                    initial_path=os.getcwd(),
                    restrict_navigation=True,
                ),
            }
        )
        .form(validate=_form_validator)
    )

    mo.accordion({"Configure Scripts Discovery Scope (TODO: Make this auto-run on load)": form})
    return (
        DECORATOR_NAME_TEXT_AREA_FORM_FIELD,
        EXCLUDE_FILE_BROWSER_FORM_FIELD,
        form,
    )


@app.cell
def _(
    DECORATOR_NAME_TEXT_AREA_FORM_FIELD,
    EXCLUDE_FILE_BROWSER_FORM_FIELD,
    find_decorated_objects,
    form,
    os,
):
    if form.value:
        _decorator_name = form.value[DECORATOR_NAME_TEXT_AREA_FORM_FIELD]
        # module_or_package = mo.notebook_dir()
        _curr_path = os.getcwd()
        _files_to_exclude = {
            f.path[len(_curr_path) + 1 :] for f in form.value[EXCLUDE_FILE_BROWSER_FORM_FIELD]
        }
        commands = find_decorated_objects(_curr_path, _decorator_name, exclude=_files_to_exclude)
    else:
        commands = []
    # commands
    return (commands,)


@app.cell
def _(mo):
    import click
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Checkbox:
        ui_elem: mo.ui.checkbox
        is_flag: bool

    RENDERED_OPTION_SELECT = (
        mo._plugins.ui._impl.input.text | mo.ui.number | mo.ui.number | Checkbox | mo.ui.dropdown
    )

    CLICK_TYPE_TO_MARIMO_UI = {
        click.STRING: mo.ui.text,
        click.INT: mo.ui.number,
        click.FLOAT: mo.ui.number,
        click.BOOL: mo.ui.checkbox,
        click.Choice: mo.ui.dropdown,
    }

    def render_option_input(opt: click.Option):
        default = opt.default
        opts = opt.opts
        required = opt.required
        help = opt.help

        match opt.type:
            case click.STRING:
                ui_element = CLICK_TYPE_TO_MARIMO_UI[click.STRING](
                    placeholder=default if default and not required else "",
                    label=("" if required else "(Optional) ") + "/".join(opts),
                )
            case click.INT:
                ui_element = CLICK_TYPE_TO_MARIMO_UI[click.INT](
                    value=default if default is not None else 0,
                    label=("" if required else "(Optional) ") + "/".join(opts),
                )  # Default to 0 if no default is provided for int
            case click.FLOAT:
                ui_element = CLICK_TYPE_TO_MARIMO_UI[click.FLOAT](
                    value=default if default is not None else 0.0,
                    label=("" if required else "(Optional) ") + "/".join(opts),
                )  # Default to 0.0 if no default for float
            case click.BOOL:
                ui_element = Checkbox(
                    ui_elem=CLICK_TYPE_TO_MARIMO_UI[click.BOOL](
                        value=bool(default) if default is not None else False,
                        label=("" if required else "(Optional) ") + "/".join(opts),
                    ),  # Default to False if no default for bool
                    is_flag=opt.is_flag,
                )
            case click.Choice(choices=choices):
                ui_element = CLICK_TYPE_TO_MARIMO_UI[click.Choice](
                    options=choices,  # Extract choices from click.Choice type
                    label=("" if required else "(Optional) ") + "/".join(opts),
                    searchable=len(choices) >= 5,
                    value=default,
                )
            case _:
                raise ValueError(f"Encountered Unsupported Option Types: {opt}")

        return ui_element

    return (
        CLICK_TYPE_TO_MARIMO_UI,
        Checkbox,
        RENDERED_OPTION_SELECT,
        click,
        dataclass,
        render_option_input,
    )


@app.cell
def show_cmd_output(Checkbox, RENDERED_OPTION_SELECT):
    import traceback

    def render_options(
        params_select: dict[str, RENDERED_OPTION_SELECT],
    ) -> list[str]:
        rendered_options = []
        for option, ui_select in params_select.items():
            match ui_select:
                case Checkbox(ui_elem=ui_elem, is_flag=is_flag) if is_flag == True:
                    if ui_elem.value:
                        rendered_options.append(option)
                case _ if ui_select.value:
                    rendered_options.append(option)
                    rendered_options.append(str(ui_select.value))
        return rendered_options

    return render_options, traceback


@app.cell
def _(Checkbox, commands, mo, render_option_input):
    def _generate_help(command):
        """Generates a formatted help string for a Click command."""
        # Create a dummy context
        ctx = command.make_context(command.name, [])  # Important!
        # Get the help string using the context
        return command.get_help(ctx)

    _run_cmd_button_enabled = len(commands) >= 1
    run_cmd_button = mo.ui.run_button(
        disabled=not _run_cmd_button_enabled,
        label="Run Command!",
        tooltip="Run the selected command.",
    )
    if commands:
        tab_params = {}
        _tabs = {}
        for _com, _location in sorted(commands, key=lambda _t: _t[0].name):
            _params_select = {_opt.opts[0]: render_option_input(_opt) for _opt in _com.params}
            tab_params[_com.name] = _params_select

            _tabs[_com.name] = mo.vstack(
                [
                    mo.md(f"""
    ```bash
    Location: {_location}

    {_generate_help(_com)}
    ```
    """),
                    # Options selection UI.
                    *[
                        (_p.ui_elem if isinstance(_p, Checkbox) else _p)
                        for _p in _params_select.values()
                    ],
                    run_cmd_button,
                ]
            )
        cmd_tabs = mo.ui.tabs(
            tabs=_tabs,
            lazy=True,
        )
    else:
        tab_params = None
        cmd_tabs = None
    cmd_tabs
    return cmd_tabs, run_cmd_button, tab_params


@app.cell
def _(
    cmd_tabs,
    commands,
    mo,
    render_options,
    run_cmd_button,
    tab_params,
    traceback,
):
    if run_cmd_button.value:
        try:
            with mo.capture_stdout() as _stdout, mo.capture_stderr() as _stderr:
                try:
                    picked_cmd = next(_c for _c in commands if _c[0].name == cmd_tabs.value)[0]
                    picked_cmd.main(
                        args=render_options(params_select=tab_params[cmd_tabs.value]),
                        standalone_mode=False,  # Don't auto-exit the interpreter on finish.
                    )
                except Exception:
                    traceback.print_exc()

                _fmtd_out = ""
                if _out := _stdout.getvalue():
                    _fmtd_out = f"""
    StdOut
    ```bash
    {_out}
    ```
    """
                _fmtd_err = ""
                if _err := _stderr.getvalue():
                    _fmtd_err = f"""
    StdErr
    ```bash
    {_err}
    ```
    """
                _output = mo.md(f"""
    # Command Output
    {_fmtd_out}

    {_fmtd_err}
    """)
        except SystemExit:
            pass
    else:
        _output = None
    _output
    return (picked_cmd,)


if __name__ == "__main__":
    app.run()
