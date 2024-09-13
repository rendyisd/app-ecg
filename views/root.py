import tkinter
import customtkinter
from PIL import Image, ImageTk

from .slide_panel import SlidePanel
from .animated_button import AnimatedButton

class Root(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("")
        self.geometry(f"{1100}x{580}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_slide_panel = SlidePanel(self, -0.25, 0)

        image_slide_panel = customtkinter.CTkImage(Image.open("assets/white_sidepanel.png"))
        self.btn_slide_panel = AnimatedButton(
            master=self,
            image=image_slide_panel,
            text="",
            width=40,
            height=40,
            fg_color="#444444",
            on_hover="#000000",
            transition_delay=100,
        )
        self.btn_slide_panel.place(x=15, y=15)

