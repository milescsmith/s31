import datetime
from dateutil.relativedelta import relativedelta
import boto3
import customtkinter as ck
from loguru import logger

from s31.aws_classes import Reservation
from s31.logging import init_logger

GPU_TYPES = ["p5", "p4", "p3", "p2", "g5g", "g5", "g4dn", "g4ad", "g3", "trn1", "inf1", "dl1", "dl2q", "f1", "vt1"]

POLL_FREQUENCY = 500

APP_FOREGROUND_COLOR = "#DDDDDD"
SUBFRAME_FOREGROUND_COLOR = "#999999"

FRAME_PADX=5
FRAME_PADY=5

SUBELEMENT_PADX=5
SUBELEMENT_PADY=5
# ck.set_default_color_theme("green")

class App(ck.CTk):
    def __init__(self, width=325, height=200):
        super().__init__(fg_color=APP_FOREGROUND_COLOR)
        self.title("GPU starter")
        self.geometry(f"{width}x{height}")

        # configure grid system
        # self.grid_rowconfigure(list(range(6)), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create and initialize variables that will get updated
        # self.status, self.uptime, self.max_uptime, and self.time_remaining are
        # needed for UI updates
        self.status = ck.StringVar()
        self.status.set("-")
        self.uptime = ck.Variable()
        self.uptime.set("--:--:--")
        self.max_uptime = ck.DoubleVar()
        self.max_uptime.set(datetime.timedelta(minutes=24).total_seconds())
        self.time_remaining = ck.DoubleVar()
        logger.debug(f"setting time_remaining to {self.max_uptime.get()}")
        self.time_remaining.set(self.max_uptime.get())

        logger.debug(f"{self.max_uptime.get()=}")
        logger.debug(f"{self.time_remaining.get()=}")

        self.build_instance_dict()

        # wrap this up in a function for cleanliness/organization
        self.build_gui()

        # Set the selected instance to the first item in the list
        self.instance_frame.selected_instance.set(self._gpu_instances[1])
        self.instance_frame.instance_box.configure(values=self._gpu_instances)
        self.set_instance()
        logger.info(f"{self.selected_instance=}")

        # most of the app loop happens in this function
        self.update_ui()

        # Set the time left label
        self.status_frame.timeremaining_value_label.configure(text=f"{self.max_uptime.get():.2f}")
        self.time_remaining_frame.time_remaining_bar.set(self.max_uptime.get())


    def build_instance_dict(self):
        # Setup interface with AWS
        self.ec2 = boto3.client("ec2")
        self.ec2_client = Reservation(self.ec2)
        self.selected_instance = None

        # get the instances that have a GPU and put them in the list that will be used
        # in the gui dropbox
        self._gpu_instances = [
            self.ec2_client[_].Name
            for _ in self.ec2_client.InstanceDict
            if self.ec2_client[_].instance_type.split(".")[0].lower() in GPU_TYPES
        ]
        # self.instances =

    def set_instance(self):
        self.selected_instance = self.ec2_client[self.instance_frame.selected_instance.get()]
        self.update_status()
        logger.debug(f"instance changed to {self.instance_frame.selected_instance.get()}")

    def update_ui(self):
        if self.selected_instance:
            self.update_status()
            if self.selected_instance.state == "running":
                self.update_uptime()
                logger.debug(f"{self.selected_instance.uptime=}")
                if self.selected_instance.auto_shutdown:
                    self.update_timeleft()
                    logger.debug(f"{self.selected_instance.time_left=}")

                    if (self.selected_instance.time_left_raw.total_seconds() <= 0) and (self.override_frame.override_cbox.get() == "off"):
                        self.selected_instance.stop_instance()
                        self.time_remaining.set(0)
                    else:
                        self.update_progressbar()

            else:
                self.status_frame.timeremaining_value_label.configure(text="--:--:--")
                self.time_remaining_frame.time_remaining_bar.configure(progress_color="grey")

        else:
            self.status_frame.timeremaining_value_label.configure(text="--:--:--")
        self.after(POLL_FREQUENCY, self.update_ui)

    def update_status(self):
        old_status = self.selected_instance.state # I don't need a heatbeat or noise in the log
        self.selected_instance.update_status()
        if self.selected_instance.state != old_status:
            logger.debug(f"{self.selected_instance.state=}")
            self.update_status()
        self.status_frame.status_value_label.configure(text=self.selected_instance.state)


    def update_uptime(self):
        self.selected_instance._update_uptime()
        self.uptime.set(self.selected_instance.uptime)
        self.status_frame.uptime_value_label.configure(text=self.uptime.get())

    def update_timeleft(self):
        logger.debug(f"{self.selected_instance.auto_shutdown=}")
        self.selected_instance._update_time_left()
        logger.debug(f"Setting time_remaining to {self.selected_instance.time_left_raw.total_seconds()}")
        self.time_remaining.set(self.selected_instance.time_left_raw.total_seconds())
        self.status_frame.timeremaining_value_label.configure(text=self.selected_instance.time_left)

    def update_progressbar(self):
        if self.selected_instance.auto_shutdown:
            logger.debug(f"{self.time_remaining.get()=}")
            logger.debug(f"{self.max_uptime.get()=}")
            remaining_time_fraction = self.time_remaining.get()/self.max_uptime.get()
            TICK_TOCK_MOTHERFUCKER = 0.1
            logger.debug(f"{remaining_time_fraction=}")
            if remaining_time_fraction <= TICK_TOCK_MOTHERFUCKER:
                self.time_remaining_frame.time_remaining_bar.configure(progress_color="red")
            else:
                self.time_remaining_frame.time_remaining_bar.configure(progress_color="green")
            self.time_remaining_frame.time_remaining_bar.set(remaining_time_fraction)
        else:
            self.time_remaining_frame.time_remaining_bar.configure(progress_color="grey")

    def build_gui(self):
        self.instance_frame = InstanceFrame(self,)
        self.instance_frame.grid(
            row=0,
            column=0,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
            sticky="ew",
            )

        self.status_frame = StatusFrame(self,)
        self.status_frame.grid(
            row=1,
            column=0,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
            sticky="ew",
            )

        self.button_frame = StartStopFrame(self,)
        self.button_frame.grid(
            row=2,
            column=0,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
            sticky="ew",
            )

        self.slider_frame = TimeLimitFrame(self,)
        self.slider_frame.grid(
            row=3,
            column=0,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
            sticky="ew",
            )
        self.slider_frame.slider.set(24)

        self.override_frame = OverrideFrame(self,)
        self.override_frame.grid(
            row=4,
            column=0,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
            sticky="ew",
            )

        # Create the progressbar that counts down until shutdown
        self.time_remaining_frame = CountdownFrame(self,)
        self.time_remaining_frame.grid(
            row=5,
            column=0,
            padx=FRAME_PADX,
            pady=FRAME_PADY,
            sticky="ew",
            )

# Frames group the UI elements together
class InstanceFrame(ck.CTkFrame):
    def __init__(self, master, fg_color=SUBFRAME_FOREGROUND_COLOR,):
        super().__init__(master, fg_color=fg_color,)

        self.selected_instance = ck.StringVar(value="")
        self.instance_box = ck.CTkComboBox(
            self,
            command=self.set_value,
            values=[""],
            variable=self.selected_instance,
        )
        self.instance_box.grid(
            row=0,
            column=0,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            sticky="news",
            )

    def set_value(self, selected_option,):
        self.selected_instance.set(selected_option,)
        logger.debug(f"{self.selected_instance.get()=}",)
        self.master.set_instance()
        self.master.update_status()


class StatusFrame(ck.CTkFrame):
    def __init__(self, master, fg_color=SUBFRAME_FOREGROUND_COLOR,):
        super().__init__(master, fg_color=fg_color,)

        self.grid_columnconfigure((0,1,2), weight=1,)

        self.status_label = ck.CTkLabel(
            self,
            text="Status:",
            justify="center",
            )
        self.status_label.grid(
            row=0,
            column=0,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            ipadx=0,
            )

        self.status_value_label = ck.CTkLabel(
            self,
            text="-",
            )
        self.status_value_label.grid(
            row=1,
            column=0,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            ipadx=0,
            )

        self.uptime_label = ck.CTkLabel(
            self,
            text="Up time:",
            )
        self.uptime_label.grid(
            row=0,
            column=1,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            ipadx=0,
            )

        self.uptime_value_label = ck.CTkLabel(
            self,
            text=self.master.uptime.get(),
            )
        self.uptime_value_label.grid(
            row=1,
            column=1,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            ipadx=0,
            )

        self.timeremaining_label = ck.CTkLabel(
            self,
            text="Time remaining:",
            )
        self.timeremaining_label.grid(
            row=0,
            column=2,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            ipadx=0,
            )

        self.timeremaining_value_label = ck.CTkLabel(
            self,
            text=self.master.time_remaining.get(),
            )
        self.timeremaining_value_label.grid(
            row=1,
            column=2,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            ipadx=0,
            )


class StartStopFrame(ck.CTkFrame):
    def __init__(self, master, fg_color=SUBFRAME_FOREGROUND_COLOR,):
        super().__init__(master, fg_color=fg_color,)

        self.start_button = ck.CTkButton(
            self,
            text="Start",
            command=self.start_callback,
            )
        self.start_button.grid(
            row=0,
            column=0,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            )
        self.stop_button = ck.CTkButton(
            self,
            text="Stop",
            command=self.stop_callback,
            )
        self.stop_button.grid(
            row=0,
            column=1,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            )

    def start_callback(self):
        self.master.instance.start_instance()
        self.master.update_status()
        logger.debug(f"{self.master.instance.State=}",)

    def stop_callback(self):
        self.master.instance.stop_instance()
        self.master.update_status()
        logger.debug(f"{self.master.instance.State=}",)


class TimeLimitFrame(ck.CTkFrame):
    def __init__(self, master, fg_color=SUBFRAME_FOREGROUND_COLOR,):
        super().__init__(master, fg_color=fg_color,)

        # row 1
        self.frame_label = ck.CTkLabel(self, text="Maximum uptime (in hours):",)
        self.frame_label.grid(
            row=0,
            column=0,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            columnspan=1,
            )

        # row 2
        self.slider = ck.CTkSlider(
            self,
            from_=1,
            to=24,
            number_of_steps=23,
            command=lambda x: self.change_max_uptime(x),
            hover=True,
        )
        self.slider.grid(
            row=1,
            column=0,
            sticky="e",
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            columnspan=2,
            )

        self.slider_val_label = ck.CTkLabel(
            self,
            text="24",
            )
        self.slider_val_label.grid(
            row=1,
            column=2,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            sticky="w",
            columnspan=1,
            )

        # row 3
        self.current_limit_label = ck.CTkLabel(
            self,
            text="Current time limit:",
            padx=SUBELEMENT_PADX,
            justify="left",
            )
        self.current_limit_label.grid(
            row=2,
            column=0,
            padx=SUBELEMENT_PADX,
            sticky="we",
            columnspan=1,
            )

        self.new_limit_label = ck.CTkLabel(
            self,
            text="New time limit (h):",
            padx=SUBELEMENT_PADX,
            )
        self.new_limit_label.grid(
            row=2,
            column=2,
            padx=SUBELEMENT_PADX,
            sticky="we",
            columnspan=1,
            )

        # row 4
        self.current_limit_value_label = ck.CTkLabel(
            self,
            text=self.master.max_uptime.get(),
            justify="center",
            )
        self.current_limit_value_label.grid(
            row=3,
            column=0,
            padx=SUBELEMENT_PADX,
            columnspan=1,
            sticky="w",
            )


        self.new_limit_value_label = ck.CTkLabel(
            self,
            text=int(self.slider.get()),
            justify="center"
            )

        self.new_limit_value_label.grid(
            row=3,
            column=2,
            padx=SUBELEMENT_PADX,
            sticky="e",
            )


    def change_max_uptime(self, max_uptime):
        logger.debug(f"Max_uptime is currently: {self.master.max_uptime.get()}")
        self.master.max_uptime.set(max_uptime)
        self.slider_val_label.configure(text=int(self.master.max_uptime.get()))
        self.new_limit_value_label.configure(text=int(self.master.max_uptime.get()))


class OverrideFrame(ck.CTkFrame):
    def __init__(self, master, fg_color=SUBFRAME_FOREGROUND_COLOR):
        super().__init__(master, bg_color="transparent", fg_color=fg_color)

        self.reset_button = ck.CTkButton(self, text="Set/Reset limit", command=self.reset_callback)
        self.reset_button.grid(row=0, column=0, padx=SUBELEMENT_PADX, pady=SUBELEMENT_PADY)
        self.override_var = ck.StringVar(value="off")
        self.override_cbox = ck.CTkCheckBox(
            self,
            text="Override Shutdown",
            command=self.on_click,
            variable=self.override_var,
            onvalue="on",
            offvalue="off",
        )
        self.override_cbox.grid(row=0, column=1, padx=SUBELEMENT_PADX, pady=SUBELEMENT_PADY,)

    def on_click(self):
        match self.master.instance.AutoShutdown:
            case True:
                self.master.instance.AutoShutdown = False
            case False:
                self.master.instance.AutoShutdown = True
        if self.override_cbox.get() == "off":
            self.master.update_progressbar()

    def reset_callback(self):
        if self.master.instance.State == "running":
            logger.debug(f"Setting max_uptime to: {self.master.instance.MaxHoursUp}")
        self.master.instance.MaxHoursUp = self.master.max_uptime.get()
        logger.debug(f"{self.instance.max_uptime.get()=}")
        self.master.instance.ResetTimeLeft()
        self.master.update_status()
        self.master.update_progressbar()
        logger.debug(f"Maximum uptime is: {self.master.instance.MaxHoursUp}")
        logger.debug(f"Maximum uptime reset. {self.master.instance.TimeLeft} remains.")
        logger.debug(f"Raw time left: {self.master.instance.TimeLeftRaw}")


class CountdownFrame(ck.CTkFrame):
    def __init__(self, master, fg_color=SUBFRAME_FOREGROUND_COLOR):
        super().__init__(master, bg_color="transparent", fg_color=fg_color)

        self.time_remaining_bar = ck.CTkProgressBar(
            self,
            orientation="horizontal",
            variable=self.master.time_remaining,
            mode="determinate",
            progress_color="green"
        )
        self.time_remaining_bar.grid(
            row=0,
            column=0,
            padx=SUBELEMENT_PADX,
            pady=SUBELEMENT_PADY,
            sticky="we"
            )

def tkgui(log_level: int = 3, save_log: bool = False):
    init_logger(verbose=log_level, save_log=save_log)
    app = App(width=320, height=400)
    app.mainloop()


if __name__ == "__main__":
    tkgui()
