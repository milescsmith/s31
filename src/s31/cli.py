from enum import Enum
from typing import Annotated

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table
import boto3

from s31 import __version__
from s31.ctk import tkgui
from s31.logging import init_logger
from s31.psgui import psgui
from s31.aws_classes import Reservation

console = Console()


class GUIType(str, Enum):
    TK = "TK"
    PSG = "PSG"
    CLI = "CLI"
    TUI = "TUI"


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
def start_gui(
    machine_name: Annotated[str, typer.Argument(help="name of the virtual machine to control")] = "Arbiter",
    gui_type: Annotated[
        GUIType,
        typer.Option(
            "-g",
            "--gui_type",
            help="Which gui interface to use. Transitional as this moves away from pysimplegui",
        ),
    ] = GUIType.CLI,
) -> None:
    init_logger(3, save_log=False)
    logger.info("COMPUTER - TEA, EARL GREY, HOT.")
    match gui_type:
        case GUIType.PSG:
            logger.info("I SUGGEST FEATHER TOUCH")
            psgui(machine_name)
        case GUIType.TK:
            logger.info("YOU HAVE SELECTED... POWER DRIVE.")
            tkgui()
        case GUIType.TUI:
            logger.info("NOT IN THE 'MOOD'?! 'MOODS' ARE FOR CATTLE AND LOVEPLAY...")
            pass
            # tui()
        case GUIYType.CLI:
            logger.info("BALL IS IN THE PARKING LOT.")
            pass
            # cli()
        case _:
            pass

@app.command(help="List and describe available EC2 instances")
def list_machines() -> list[str]:
    ec2 = boto3.client("ec2")
    ec2_client = Reservation(ec2)
    
    table = Table(title="EC2 instances")
    table.add_column("Name",justify="right", style="cyan", no_wrap=True)
    table.add_column("InstanceType", style="magenta")
    table.add_column("State", justify="right", style="green")

    for _ in ec2_client.Instances:
        table.add_row(_.Name, _.instance_type, _.state)

    console = Console()
    console.print(table)

def start_machine(machine: str):
    ...

def stop_machine(machine: str):
    ...

def machine_status(machine: list[str] | str | None = None):
    ...

def alter_time_limit(machine: str):
    ...

