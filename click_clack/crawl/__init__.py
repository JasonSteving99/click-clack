import ast
from importlib import import_module
import os
import sys
from typing import Any


def _find_in_ast(node, current_module_path, decorated_objects: list[Any]):
    match node:
        case (
            ast.FunctionDef(decorator_list=decorators)
            | ast.AsyncFunctionDef(decorator_list=decorators)
        ) if any(_is_click_command(d) for d in decorators):
            func_name = node.name
            try:  # Handle potential import errors
                imported_module = import_module(current_module_path.replace("/", ".")[:-3])
                decorated_objects.append(
                    (
                        imported_module.__dict__[func_name],
                        current_module_path,
                    )
                )
            except Exception as e:
                print(f"Failed to import click command for some reason: {e}", file=sys.stderr)
                pass  # Or handle differently if needed


def _find_decorated_objects_in_source(
    source: str, current_module_path: str, decorated_objects: list[Any]
):
    tree = ast.parse(source)
    for top_level_node in tree.body:
        _find_in_ast(
            top_level_node,
            current_module_path=current_module_path,
            decorated_objects=decorated_objects,
        )


def _is_click_command(decorator: ast.expr) -> bool:
    """Check if a decorator is click.command()."""
    match decorator:
        # Match click.command()
        case ast.Call(func=ast.Attribute(value=ast.Name(id="click"), attr="command")):
            return True
        # Also match imported command, like: from click import command
        case ast.Call(func=ast.Name(id="command")):
            # TODO: This is a simplification - we really should check imports.
            return True
        case _:
            return False


def _process_module(file_path: str, module_path: str, decorated_objects: list[Any]):
    with open(file_path, "r") as f:
        _find_decorated_objects_in_source(f.read(), module_path, decorated_objects)


def crawl_click_commands(module_path, exclude):
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

    if os.path.isdir(module_path):  # Handle packages (directories)
        for root, _, files in os.walk(module_path):
            # We're traversing all dirs below the given module_path, so we need to check if it's a hidden dir, and avoid it if so.
            root_suffix = root[len(os.path.commonpath([module_path, root])) + 1 :]
            if root_suffix.startswith("."):
                continue  # Skip this hidden dir.
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    if full_path in exclude:
                        continue
                    _process_module(
                        file_path=full_path,
                        module_path=os.path.join(root_suffix, file),
                        decorated_objects=decorated_objects,
                    )
    else:
        raise ValueError("Invalid module path. Must be a directory.")

    return decorated_objects
