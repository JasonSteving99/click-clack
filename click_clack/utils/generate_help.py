import click
import asyncclick.core


async def generate_help(command):
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
