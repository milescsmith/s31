from .psgui import psgui
from typing import Annotated
import typer
from . import s31


@s31.command(no_args_is_help=True)
def main(
    machine_name: Annotated[
        str, typer.Argument(help="name of the virtual machine to control")
    ] = "Arbiter",
    gui_type: Annotated[
        str,
        typer.Option(
            "-g",
            "--gui_type",
            help="Which gui interface to use. Transitional as this moves away from pysimplegui",
        ),
    ] = "PSG",
) -> None:
    match gui_type:
        case "PSG":
            psgui(machine_name)
        case _:
            pass


if __name__ == "__main__":
    s31()
