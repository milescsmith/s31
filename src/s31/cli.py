from loguru import logger
from typing import Annotated
import typer
from rich.console import Console
from enum import Enum

from s31 import __version__
from s31.psgui import psgui
from s31.ctk import tkgui
from s31.logging import init_logger

console = Console()

class GUIType(str, Enum):
    TK = "TK"
    PSG = "PSG"

def version_callback(value: bool) -> None:
    """Prints the version of the package."""
    if value:
        console.print(f"[yellow]fcsjanitor[/] version: [bold blue]{__version__}[/]")
        raise typer.Exit()

app = typer.Typer(
    name="s31",
    help=("Turn on/shut off AWS VMs"),
    add_completion=False,
    rich_markup_mode="markdown",
    no_args_is_help=True,
)

@app.command(no_args_is_help=True)
def main(
    machine_name: Annotated[
        str, typer.Argument(help="name of the virtual machine to control")
    ] = "Arbiter",
    gui_type: Annotated[
        GUIType,
        typer.Option(
            "-g",
            "--gui_type",
            help="Which gui interface to use. Transitional as this moves away from pysimplegui",
        ),
    ] = GUIType.PSG,
) -> None:
    init_logger(3, save_log=False)
    logger.info("HELLO SEATTLE!")
    match gui_type:
        case GUIType.PSG:
            psgui(machine_name)
        case GUIType.TK:
            tkgui()
        case _:
            pass
