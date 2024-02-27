import customtkinter as ck
from loguru import logger
from s31.logging import init_logger
import boto3
from s31.aws_classes import Reservation
import datetime

GPU_TYPES = [
    "p5", "p4", "p3", "p2",
    "g5g", "g5", "g4dn", "g4ad", "g3",
    "trn1",
    "inf1",
    "dl1",
    "dl2q",
    "f1",
    "vt1"
]

POLL_FREQUENCY = 1000

class InstanceFrame(ck.CTkFrame):
    def __init__(self, master, width=300, height=36):
        super().__init__(master, width=width, height=height)

        self.selected_instance = ck.StringVar(value="")
        self.instance_box = ck.CTkComboBox(
            self,
            command=self.show_value,
            values=[""],
            variable=self.selected_instance,
            width=width,
        )
        self.instance_box.grid(row=0, column=0, padx=10, pady=5)

    def show_value(self, selected_option):
        print(selected_option)


class StatusFrame(ck.CTkFrame):
    def __init__(self, master, width=300):
        super().__init__(master, width=width)

        self.status_label = ck.CTkLabel(self, text="Status:")
        self.status_label.grid(row=0, column=0, padx=10, pady=5)

        self.status_value_label = ck.CTkLabel(self, text="stopped")
        self.status_value_label.grid(row=1, column=0, padx=10, pady=5)

        self.uptime_label = ck.CTkLabel(self, text="Up time:")
        self.uptime_label.grid(row=0, column=1, padx=10, pady=5)

        self.uptime_value_label = ck.CTkLabel(self, text="None")
        self.uptime_value_label.grid(row=1, column=1, padx=10, pady=5)

        self.timeremaining_label = ck.CTkLabel(self, text="Time remaining:")
        self.timeremaining_label.grid(row=0, column=2, padx=10, pady=5)

        self.timeremaining_value_label = ck.CTkLabel(self, text="-")
        self.timeremaining_value_label.grid(row=1, column=2, padx=10, pady=5)


class ButtonFrame(ck.CTkFrame):
    def __init__(self, master, width=300, button_width=100):
        super().__init__(master, width=width)

        button_x_padding = (width - button_width * 2) / 8
        self.start_button = ck.CTkButton(
            self, text="Start", width=button_width, command=self.start_callback
        )
        self.start_button.grid(row=0, column=0, padx=button_x_padding, pady=5)
        self.stop_button = ck.CTkButton(
            self, text="Stop", width=button_width, command=self.stop_callback
        )
        self.stop_button.grid(row=0, column=1, padx=button_x_padding, pady=5)

    def start_callback(self):
        pass

    def stop_callback(self):
        pass


class SliderFrame(ck.CTkFrame):
    def __init__(self, master, width=300):
        super().__init__(master, width=width)

        self.slider = ck.CTkSlider(self, width=width, from_=0, to=24, command=None)
        self.slider.grid(row=0, column=0, sticky="nws")


class CheckboxFrame(ck.CTkFrame):
    def __init__(self, master, width=300):
        super().__init__(master, width=width, bg_color="transparent")

        self.override_var = ck.StringVar(value="off")
        self.override_cbox = ck.CTkCheckBox(
            self,
            width=width,
            text="Override Shutdown",
            command=self.on_click,
            variable=self.override_var,
            onvalue="on",
            offvalue="off",
        )
        self.override_cbox.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="new")

    def on_click(self):
        logger.debug(self.override_cbox.get())
        logger.debug(self.override_var.get())
        if self.override_cbox.get() == "off":
            self.master.update_progressbar()


class ProgressFrame(ck.CTkFrame):
    def __init__(self, master, width=300, amount_of_time=0):
        super().__init__(master, width=width, fg_color="transparent")

        self.time_left = ck.DoubleVar()
        self.time_left.set(amount_of_time)

        self.time_left_label = ck.CTkLabel(self, text="", fg_color="transparent")
        self.time_left_label.grid(row=0, column=0, sticky="nws")
        self.time_remaining_bar = ck.CTkProgressBar(
            self,
            width=width,
            orientation="horizontal",
            variable=self.time_left,
            mode="determinate",
        )
        self.time_remaining_bar.grid(row=1, column=0, sticky="nws")


class App(ck.CTk):
    def __init__(self, width=325, height=200):
        super().__init__()
        self.title("GPU starter")
        self.geometry(f"{width}x{height}")

        self.instance_frame = InstanceFrame(self, width=240)
        self.instance_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.status_frame = StatusFrame(self, width=350)
        self.status_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.button_frame = ButtonFrame(self, width=300, button_width=110)
        self.button_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.slider_frame = SliderFrame(self, width=260)
        self.slider_frame.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.override_frame = CheckboxFrame(self, width=250)
        self.override_frame.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.time_remaining = 1
        self.time_remaining_frame = ProgressFrame(self, width=260)
        self.time_remaining_frame.grid(
            row=5, column=0, padx=10, pady=(10, 0), sticky="nws"
        )
        self.time_remaining_frame.time_left_label.configure(
            text=f"{self.time_remaining:.2f}"
        )
        self.time_remaining_frame.time_remaining_bar.set(self.time_remaining)

        self.ec2 = boto3.client("ec2")
        self.ec2_client = Reservation(self.ec2)
        # This seems like it SHOULD work, but for some reason it does not return values for the instances I am using that
        # DO have gpus
        # gpu_types = [_["InstanceType"] for _ in ec2.describe_instance_types()["InstanceTypes"] if "GpuInfo" in _.keys()]
        _gpu_instances = [
            self.ec2_client[_].Name
            for _ 
            in self.ec2_client.InstanceDict 
            if self.ec2_client[_].InstanceType.split(".")[0].lower() in GPU_TYPES
            ]

        self.instance_frame.selected_instance.set(_gpu_instances[1])
        self.instance_frame.instance_box.configure(values=_gpu_instances)
        
        self.update_progressbar()
        self.update_uptime()

    def update_progressbar(self):
        self.time_remaining -= 0.01
        self.time_remaining_frame.time_left_label.configure(
            text=f"{self.time_remaining:.2f}"
        )
        self.time_remaining_frame.time_remaining_bar.set(self.time_remaining)

        if (self.time_remaining > 0) and (self.override_frame.override_cbox.get() == "off"):
            self.after(100, self.update_progressbar)
        else:
            self.time_remaining_frame.time_left_label.configure(text="Time's up!")
    
    def update_uptime(self):
        pass

def tkgui():
    init_logger(verbose=3, save_log=False)
    app = App(width=275, height=325)
    app.mainloop()
    
if __name__ == "__main__":
    tkgui()
