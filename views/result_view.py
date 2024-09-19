import customtkinter

import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .animated_button import AnimatedButton

class ResultView(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        # fig = plt.Figure(figsize=(28, 4), dpi=100)
        # ax = fig.add_subplot(111)
        # ax.plot([0, 1, 2, 3], [10, 1, 4, 9], label="Line")
        # ax.set_title("Sample Plot")
        # ax.set_xlabel("X-axis")
        # ax.set_ylabel("Y-axis")
        # ax.legend()

        # canvas = FigureCanvasTkAgg(fig, master=self)  # A canvas for embedding the figure
        # canvas.draw()  # Drawing the canvas
        # canvas.get_tk_widget().pack(fill="both", expand=True)

        