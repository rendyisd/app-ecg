import customtkinter

import matplotlib.pyplot as plt

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .animated_button import AnimatedButton

class ResultView(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=1)

        self._font_form_fieldname = customtkinter.CTkFont(
            family="Bahnschrift",
            size=16,
            weight="bold"
        )

        self.canvas = FigureCanvasTkAgg(Figure(figsize=(28, 5)), master=self) # placeholder
        self.canvas.get_tk_widget().grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

        self.btn = AnimatedButton(
            master=self,
            text="Testing",
            font=self._font_form_fieldname,
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )

        self.btn.grid(row=1, column=0, sticky="n")

    
    def new_canvas(self, fig):
        self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, padx=50, pady=50, sticky="nsew")

        