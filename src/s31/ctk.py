import customtkinter as ck


class InstanceFrame(ck.CTkFrame):
    def __init__(self, master, width=300):
        super().__init__(master, width=width)
        
        self.selected_instance = ck.StringVar(value="Arbiter")
        self.instance_box = ck.CTkComboBox(
            self,
            command=self.show_value, 
            values=["Arbiter", "Gravemind"],
            variable=self.selected_instance,
            width=width
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
            command=self.override_event,
            variable=self.override_var,
            onvalue="on",
            offvalue="off"
            )
        self.override_cbox.grid(row=0, column=0, padx=5, pady=(5,5), sticky="new")
    
    def override_event(self):
        return self.override_var.get()

class ProgressFrame(ck.CTkFrame):
    def __init__(self, master, width=300):
        super().__init__(master, width=width)

        self.time_remaining_bar = ck.CTkProgressBar(self, width=width, orientation="horizontal")
        self.time_remaining_bar.grid(row=0, column=0, sticky="nws")

class App(ck.CTk):
    def __init__(self, width=325, height=200):
        super().__init__()
        self.title("GPU starter")
        self.geometry(f"{width}x{height}")

        self.instance_frame = InstanceFrame(self, width=240)
        self.instance_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nws")
        
        self.status_frame = StatusFrame(self, width=300)
        self.status_frame.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.button_frame = ButtonFrame(self, width=300, button_width=110)
        self.button_frame.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.slider_frame = SliderFrame(self, width=260)
        self.slider_frame.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="nws")

        self.override_frame = CheckboxFrame(self, width=250)
        self.override_frame.grid(row=4, column=0, padx=10, pady=(10,0), sticky="nws")
        
        self.time_remaining_frame = ProgressFrame(self, width=260)
        self.time_remaining_frame.grid(row=5, column=0, padx=10, pady=(10,0), sticky="nws")


# TODO make configurable
app = App(width=275, height=300)
app.mainloop()
