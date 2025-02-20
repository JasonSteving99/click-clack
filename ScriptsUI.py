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
                            hasattr(decorator, "func")
                            and isinstance(decorator.func, ast.Attribute)
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

    mo.accordion({
        "Configure Scripts Discovery Scope (TODO: Make this auto-run on load)": form
    })
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
        decorator_name = form.value[DECORATOR_NAME_TEXT_AREA_FORM_FIELD]
        # module_or_package = mo.notebook_dir()
        curr_path = os.getcwd()
        files_to_exclude = {
            f.path[len(curr_path) + 1 :]
            for f in form.value[EXCLUDE_FILE_BROWSER_FORM_FIELD]
        }
        commands = find_decorated_objects(
            curr_path, decorator_name, exclude=files_to_exclude
        )
    else:
        commands = []
    commands
    return commands, curr_path, decorator_name, files_to_exclude


@app.cell
def _(commands, mo):
    pick_cmd = mo.ui.dropdown(
        options={f"{com[0].name}: {com[1]}": com[0] for com in commands},
        # options=[f"{com[0].name}: {com[1]}" for com in commands],
        label="Pick the command to run",
        searchable=len(commands) > 5,
    )
    return (pick_cmd,)


@app.cell
def _(commands, mo, pick_cmd):
    _run_cmd_button_enabled = len(commands) >= 1 and pick_cmd.value
    run_cmd_button = mo.ui.run_button(
        disabled=not _run_cmd_button_enabled,
        label="Run Command!",
        tooltip="Run the selected command.",
    )

    import click

    RENDERED_OPTION_SELECT = mo._plugins.ui._impl.input.text  # | mo._plugins.ui._impl.input.file_browser | mo._plugins.ui._impl.input.file

    def _render_option_input(opt: click.Option):
        default = opt.default
        opts = opt.opts
        required = opt.required
        help = opt.help
        match opt.type:
            case click.STRING:
                return mo.ui.text(
                    placeholder=default if default and not required else "", 
                    label=("" if required else "(Optional) ") + "/".join(opts),
                )
            case _:
                raise ValueError(f"Encountered Unsupported Option Types: {opt}")

    if pick_cmd.value:
        params_select = {opt.opts[0]: _render_option_input(opt) for opt in pick_cmd.value.params}
    else:
        params_select = {}

    mo.vstack(
        [
            pick_cmd.center(),
            *[p.center() for p in params_select.values()],
            *filter(
                None,
                [run_cmd_button.center() if _run_cmd_button_enabled else None],
            ),
        ]
    )
    return RENDERED_OPTION_SELECT, click, params_select, run_cmd_button


@app.cell
def show_cmd_output(
    RENDERED_OPTION_SELECT,
    mo,
    params_select,
    pick_cmd,
    run_cmd_button,
):
    import traceback

    def _render_options(params_select: dict[str, RENDERED_OPTION_SELECT]) -> list[str]:
        # TODO: Stop hardcoding the assumption that they all have a simple `.value` str to access.
        strings = [(option, ui_select.value) for option, ui_select in params_select.items() if ui_select.value]
        return [s for pair in strings for s in pair]

    if run_cmd_button.value:
        try:
            with mo.capture_stdout() as _stdout, mo.capture_stderr() as _stderr:
                try:
                    pick_cmd.value.main(
                        args=_render_options(params_select=params_select),
                        standalone_mode=False,  # Don't auto-exit the interpreter on finish.
                    )
                except:
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
    return (traceback,)


if __name__ == "__main__":
    app.run()
