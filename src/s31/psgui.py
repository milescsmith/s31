import PySimpleGUI as sg
import boto3
import platform
import datetime
from .aws_classes import Reservation

def psgui(instance_name: str = "Arbiter") -> None:
    sg.theme("SystemDefaultForReal")
    if platform.system() == "Windows":
        ttk_style = "vista"
    elif platform.system() == "Darwin":
        ttk_style = "aqua"
    else:
        ttk_style = "clam"

    ec2 = boto3.client("ec2")
    ec2_client = Reservation(ec2)
    instance = ec2_client[instance_name]

    layout = [
        [
            sg.Text("Status:"),
            sg.Text("Up time:"),
            sg.Text("Time Remaining:"),
        ],
        [
            sg.Text(
                f"{instance.State}",
                key="-STATE-",
            ),
            sg.Text(
                f"{instance.UpTime}",
                key="-UPTIME-",
            ),
            sg.Text(
                "-",
                key="-TIME_REMAINING-",
            ),
        ],
        [
            sg.Button(
                "Start",
                use_ttk_buttons=True,
            ),
            sg.Button(
                "Stop",
                use_ttk_buttons=True,
            ),
        ],
        [
            sg.Text(
                "VM time limit:",
            ),
            sg.Slider(
                (1, 24),
                default_value=8,
                resolution=1,
                enable_events=True,
                orientation="horizontal",
                relief="flat",
                tooltip="Maximum number of hours to allow the \nVM to run (unless overridden)",
                key="-TIMELIMIT-",
            ),
        ],
        [
            sg.Checkbox(
                "Override shutdown",
                default=False,
                tooltip="If checked, do not shutdown the machine \nafter the set number of hours",
                enable_events=True,
                key="-OVERRIDE-",
            ),
        ],
        [
            sg.ProgressBar(
                max_value=100,
                orientation="h",
                size=(32, 100),
                bar_color="green",
                key="-PROGRESS-",
                style="alt",
                expand_y=True,
            ),
        ],
    ]

    # Create the window
    window = sg.Window(
        "GPU starter", layout, ttk_theme=ttk_style, use_ttk_buttons=True, font=(16,)
    )
    POLL_FREQUENCY = 1000  # update the window every second
    PROGRESS_BAR_INITIALIZED = False
    # Create an event loop
    while True:
        event, values = window.read(timeout=POLL_FREQUENCY)
        # End program if user closes window or
        # presses the OK button
        # if not override_timeout and
        if PROGRESS_BAR_INITIALIZED is False:
            window["-PROGRESS-"].update(current_count=100, bar_color="green")
            window.refresh()
        match event:
            case "Start":
                instance.start_instance()
            case "Stop":
                instance.stop_instance()
            case sg.WIN_CLOSED:
                break
        # window["-OVERRIDE-STATUS-"].update(f"Override is {'enabled' if values['-OVERRIDE-'] else 'disabled'}")
        max_uptime = datetime.timedelta(hours=values["-TIMELIMIT-"])

        if not window["-OVERRIDE-"] and (instance.UpTimeRaw > max_uptime):
            instance.stop_instance()
            sg.popup(f"The {values['-TIMELIMIT-']}h time limit has been reached!")

        if values["-OVERRIDE-"]:
            window["-TIMELIMIT-"].update(visible=False)
            window["-PROGRESS-"].update(visible=False)
            window["-TIME_REMAINING-"].update("-")
            window.refresh()
        else:
            window["-TIMELIMIT-"].update(visible=True)
            if instance.State == "running":
                if instance.UpTimeRaw < max_uptime:
                    time_left = 100 - (instance.UpTimeRaw / max_uptime) * 100
                    window["-TIME_REMAINING-"].update(
                        str(max_uptime - instance.UpTimeRaw).split(".")[0]
                    )
                    if time_left <= 10:
                        sg.popup(
                            f"Warning! Only {str(max_uptime - instance.UpTimeRaw).split('.')[0]} remains before automatic shutdown!"
                        )
                        window["-PROGRESS-"].update(
                            visible=True, current_count=time_left, bar_color="red"
                        )
                        window["-TIME_REMAINING-"].update(text_color="red")
                    else:
                        window["-PROGRESS-"].update(
                            visible=True, current_count=time_left, bar_color="green"
                        )
            else:
                window["-STATE-"].update(text_color="red")
                window["-TIME_REMAINING-"].update("-")

        if instance.State == "running":
            window["-STATE-"].update(text_color="green")
        else:
            window["-STATE-"].update(text_color="black")
        window.refresh()
        instance.UpdateUpTime()
        window["-STATE-"].update(instance.State)
        window["-UPTIME-"].update(instance.UpTime)

    window.close()
    
if __name__ == '__main__':
    psgui("Gravemind")
