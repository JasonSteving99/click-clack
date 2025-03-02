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
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
                        except Exception:
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
def _(mo, os):
    DECORATOR_NAME_TEXT_AREA_FORM_FIELD = "decorator_name_text_area"
    EXCLUDE_FILE_BROWSER_FORM_FIELD = "exclude_file_browser"

    def _form_validator(form_json: dict[str, object]) -> str | None:
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

    mo.accordion({"[Click to reconfigure Scripts Discovery Scope]": form})
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
    _curr_path = os.getcwd()

    if form.value:
        _decorator_name = form.value[DECORATOR_NAME_TEXT_AREA_FORM_FIELD]
        # module_or_package = mo.notebook_dir()
        _files_to_exclude = {
            f.path[len(_curr_path) + 1 :] for f in form.value[EXCLUDE_FILE_BROWSER_FORM_FIELD]
        }
        commands = find_decorated_objects(_curr_path, _decorator_name, exclude=_files_to_exclude)
    else:
        # Just kick this off right away optimistically, if there are any issues, then fallback.
        try:
            commands = find_decorated_objects(_curr_path, "command", exclude={})
        except Exception:
            commands = []
    return (commands,)


@app.cell
def _(mo, os):
    import click
    import asyncclick
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Checkbox:
        ui_elem: mo.ui.checkbox
        is_flag: bool

    RENDERED_OPTION_SELECT = (
        mo._plugins.ui._impl.input.text
        | mo.ui.number
        | mo.ui.number
        | Checkbox
        | mo.ui.dropdown
        | mo.ui.file
        | mo.ui.number
    )

    def render_option_input(opt: click.Option):
        default = opt.default
        opts = opt.opts
        required = opt.required
        help = opt.help
        label = ("" if required else "(Optional) ") + "/".join(opts)

        match opt.type:
            case click.STRING | asyncclick.STRING:
                ui_element = mo.ui.text(
                    placeholder=default if default and not required else "",
                    label=label,
                )
            case click.INT | asyncclick.INT:
                ui_element = mo.ui.number(
                    value=default if default is not None else 0,
                    label=label,
                )  # Default to 0 if no default is provided for int
            case click.FLOAT | asyncclick.FLOAT:
                ui_element = mo.ui.number(
                    value=default if default is not None else 0.0,
                    label=label,
                )  # Default to 0.0 if no default for float
            case click.BOOL | asyncclick.BOOL:
                ui_element = Checkbox(
                    ui_elem=mo.ui.checkbox(
                        value=bool(default) if default is not None else False,
                        label=label,
                    ),  # Default to False if no default for bool
                    is_flag=opt.is_flag,
                )
            case click.Choice(choices=choices) | asyncclick.Choice(choices=choices):
                ui_element = mo.ui.dropdown(
                    options=choices,  # Extract choices from click.Choice type
                    label=label,
                    searchable=len(choices) >= 5,
                    value=default,
                )
            case click.File() | asyncclick.File():
                # TODO: Add support for click's more advanced features here, such as stdin via "-" and
                #       referencing files that don't necessarily exist yet.
                ui_element = mo.ui.file_browser(
                    label=label,
                    initial_path=os.getcwd(),
                    multiple=False,
                    restrict_navigation=False,  # Allow selecting arbitrary files even above curr dir.
                )
            case click.Path() | asyncclick.Path():
                ui_element = mo.ui.text(
                    placeholder=str(default)
                    if default and not required
                    else "",  # Default to string representation of default path
                    label=label,
                )
            case click.DateTime(formats=formats) | asyncclick.DateTime(formats=formats):
                ui_element = mo.ui.text(
                    placeholder=str(default) if default else "  |  ".join(formats),
                    label=label,
                    full_width=True,  # Make room to show all the formats.
                )
            case (
                click.IntRange(min=min_val, max=max_val)
                | asyncclick.IntRange(min=min_val, max=max_val)
            ):
                ui_element = mo.ui.number(
                    start=min_val,
                    stop=max_val,
                    step=1,  # Integers.
                    value=default,
                    label=label,
                )
            case (
                click.FloatRange(min=min_val, max=max_val)
                | asyncclick.FloatRange(min=min_val, max=max_val)
            ):
                ui_element = mo.ui.number(
                    start=min_val,
                    stop=max_val,
                    value=default,
                    label=label,
                )
            case _:
                raise ValueError(f"Encountered Unsupported Option Types: {opt} {opt.type}")

        return ui_element

    return (
        Checkbox,
        RENDERED_OPTION_SELECT,
        asyncclick,
        click,
        dataclass,
        render_option_input,
    )


@app.cell
def show_cmd_output(Checkbox, RENDERED_OPTION_SELECT, mo):
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
                case mo.ui.file_browser(path=path) as f:
                    rendered_options.append(option)
                    rendered_options.append(path())
                case _ if ui_select.value:
                    rendered_options.append(option)
                    rendered_options.append(str(ui_select.value))
        return rendered_options

    return render_options, traceback


@app.cell
async def _(
    Checkbox,
    asyncclick,
    click,
    commands,
    mo,
    render_option_input,
):
    from collections import Counter

    def get_cmd_tab_name(_cmd, _location, _cmd_counts: Counter):
        # It's possible that the same command name is used repeatedly in the codebase (note that this
        # "name" is actually just the name of the function decorated with @click.command() so honestly
        # it's not that surprising if it'll be duplicated). If it is, we need to distinguish them in the
        # ui somehow.
        if _cmd_counts[_cmd.name] > 1:
            return f"{_cmd.name} ({_location})"
        return _cmd.name

    async def _generate_help(command):
        """Generates a formatted help string for a Click command."""
        # Create a dummy context - we may still need to await this if in the asyncclick case this is
        # actually a coroutine object right now.
        ctx = command.make_context(
            command.name,
            [],
            # Ensure that for now we prevent this created context from throwing errors on
            # the empty args we're passing in. We can't possibly know the args yet, but we
            # don't need them since we just want the help message.
            resilient_parsing=True,
        )  # Important!
        match command:
            case click.Command():
                pass  # We're all good, no need to await.
            case asyncclick.core.Command():
                ctx = await ctx  # We need to await this call unlike with non-async click.
            case _:
                raise ValueError(f"Unexpected command type: {command} {type(command)}")
        # Get the help string using the context
        return command.get_help(ctx)

    _run_cmd_button_enabled = len(commands) >= 1
    run_cmd_button = mo.ui.run_button(
        disabled=not _run_cmd_button_enabled,
        label="Run Command!",
        tooltip="Run the selected command.",
    )
    streamed_outputs_opt_in = mo.ui.checkbox(
        label="Stream Output (for long-running commands, but worse formatting due to current Marimo limitations)"
    )
    if commands:
        command_name_counts = Counter([c[0].name for c in commands])
        tab_params = {}
        _tabs = {}
        for _com, _location in sorted(commands, key=lambda _t: _t[0].name):
            _params_select = {_opt.opts[0]: render_option_input(_opt) for _opt in _com.params}
            _cmd_tab_name = get_cmd_tab_name(_com, _location, command_name_counts)
            tab_params[_cmd_tab_name] = _params_select

            _tabs[_cmd_tab_name] = mo.vstack(
                [
                    mo.md(f"""
    ```bash
    Location: {_location}

    {await _generate_help(_com)}
    ```
    """),
                    # Options selection UI.
                    *[
                        (_p.ui_elem if isinstance(_p, Checkbox) else _p)
                        for _p in _params_select.values()
                    ],
                    run_cmd_button,
                    streamed_outputs_opt_in,
                ]
            )
        cmd_tabs = mo.ui.tabs(
            tabs=_tabs,
            lazy=True,
        )
    else:
        tab_params = None
        cmd_tabs = None
        command_name_counts = None
    cmd_tabs
    return (
        Counter,
        cmd_tabs,
        command_name_counts,
        get_cmd_tab_name,
        run_cmd_button,
        streamed_outputs_opt_in,
        tab_params,
    )


@app.cell
async def _(
    asyncclick,
    click,
    cmd_tabs,
    command_name_counts,
    commands,
    get_cmd_tab_name,
    mo,
    render_options,
    run_cmd_button,
    streamed_outputs_opt_in,
    tab_params,
    traceback,
):
    async def _run_cmd():
        picked_cmd = next(
            _c
            for _c in commands
            if get_cmd_tab_name(_c[0], _c[1], command_name_counts) == cmd_tabs.value
        )[0]
        args = {
            "args": render_options(params_select=tab_params[cmd_tabs.value]),
            "standalone_mode": False,  # Don't auto-exit the interpreter on finish.
        }
        try:
            match picked_cmd:
                case click.Command():
                    picked_cmd.main(**args)
                case asyncclick.core.Command():
                    await picked_cmd.main(**args)
        except Exception:
            # Catch any exception and render it to stdout.
            traceback.print_exc()

    if run_cmd_button.value:
        try:
            # For now, we're gonna let people opt into whether they want nice formatting or streamed
            # outputs. Ideally I wouldn't have to choose and I'd just go with redirecting in all cases,
            # but Marimo's redirect support renders as byte strings which is absolutely ugly.
            if streamed_outputs_opt_in.value:
                with mo.redirect_stdout(), mo.redirect_stderr():
                    await _run_cmd()
                _output = None
            else:
                with mo.capture_stdout() as _stdout, mo.capture_stderr() as _stderr:
                    await _run_cmd()
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
    return


if __name__ == "__main__":
    app.run()
