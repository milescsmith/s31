from importlib.metadata import PackageNotFoundError, version
from rich.console import Console
import typer

console = Console()

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

def version_callback(value: bool) -> None:
    """Prints the version of the package."""
    if value:
        console.print(f"[yellow]fcsjanitor[/] version: [bold blue]{__version__}[/]")
        raise typer.Exit()


s31 = typer.Typer(
    name="s31",
    help=("Turn on/shut off AWS VMs"),
    add_completion=False,
    rich_markup_mode="markdown",
    no_args_is_help=True,
)
