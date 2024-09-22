import customtkinter

import matplotlib.pyplot as plt

from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .animated_button import AnimatedButton
from detection.util_func import get_lead_display_name

class ResultView(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.other_result_btn = []

        self.canvas = FigureCanvasTkAgg(Figure(figsize=(28, 5)), master=self) # placeholder

        self.info_frame = customtkinter.CTkFrame(
            self,
            fg_color="#333333",
            corner_radius=20,
        )
        self.info_frame.grid_rowconfigure(0, weight=1)
        self.info_frame.grid_rowconfigure(1, weight=1)
        self.info_frame.grid_rowconfigure(2, weight=1)
        self.info_frame.grid_rowconfigure(3, weight=1)
        self.info_frame.grid_rowconfigure(4, weight=1)

        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)

        self.if_lbl_1 = customtkinter.CTkLabel(
            self.info_frame,
            text="ID Pasien: ",
            font=("Bahnschrift", 14)
        )
        self.if_lbl_2 = customtkinter.CTkLabel(
            self.info_frame,
            text="ID Hasil: ",
            font=("Bahnschrift", 14)
        )
        self.if_lbl_3 = customtkinter.CTkLabel(
            self.info_frame,
            text="Nama Pasien: ",
            font=("Bahnschrift", 14)
        )
        self.if_lbl_4 = customtkinter.CTkLabel(
            self.info_frame,
            text="Lead: ",
            font=("Bahnschrift", 14)
        )
        self.if_btn_each_beat = AnimatedButton(
            master=self.info_frame,
            text="Detail Deteksi Setiap Beat",
            font=("Bahnschrift", 12, "bold"),
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )

        self.other_result_frame = customtkinter.CTkScrollableFrame(
            self,
            fg_color="#333333",
            corner_radius=20,
        )

        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, padx=50, pady=(50, 0), sticky="nsew")

        self.info_frame.grid(row=1, column=0, columnspan=1, padx=(25, 12), pady=25, sticky="nsew")
        self.if_lbl_1.grid(row=0, column=0, columnspan=2, sticky="w", padx=10)
        self.if_lbl_2.grid(row=1, column=0, columnspan=2, sticky="w", padx=10)
        self.if_lbl_3.grid(row=2, column=0, columnspan=2, sticky="w", padx=10)
        self.if_lbl_4.grid(row=3, column=0, columnspan=2, sticky="w", padx=10)
        self.if_btn_each_beat.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10)

        self.other_result_frame.grid(row=1, column=1, columnspan=1, padx=(12, 25), pady=25, sticky="nsew")

    
    def new_canvas(self, fig):
        self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=2, padx=50, pady=(50, 0), sticky="nsew")
    
    def create_beat_toplevel(self):
        self.beat_toplevel = customtkinter.CTkToplevel(self)
        self.beat_toplevel.title("Deteksi Setiap Beat")
        self.beat_toplevel.geometry(f"{1100}x{580}")
        self.beat_toplevel.resizable(False, False)
        self.beat_toplevel.grab_set()

        self.beat_toplevel.grid_rowconfigure(0, weight=1)
        self.beat_toplevel.grid_rowconfigure(1, weight=1)

        self.beat_toplevel.grid_columnconfigure(0, weight=1)
        self.beat_toplevel.grid_columnconfigure(1, weight=1)
        self.beat_toplevel.grid_columnconfigure(2, weight=1)

        self.canvas_toplevel = FigureCanvasTkAgg(Figure(figsize=(28, 5)), master=self.beat_toplevel)

        self.btn_previous = AnimatedButton(
            master=self.beat_toplevel,
            text="<",
            font=("Bahnschrift", 18, "bold"),
            fg_color="#2A2A2A",
            on_hover="#242424",
            height=40,
            transition_delay=100
        )
        self.lbl_index = customtkinter.CTkLabel(
            self.beat_toplevel,
            text="0",
            font=("Bahnschrift", 18, "bold")
        )

        self.btn_next = AnimatedButton(
            master=self.beat_toplevel,
            text=">",
            font=("Bahnschrift", 18, "bold"),
            fg_color="#2A2A2A",
            on_hover="#242424",
            height=40,
            transition_delay=100
        )

        self.canvas_toplevel.get_tk_widget().grid(row=0, column=0, columnspan=3, padx=50, pady=(50, 25), sticky="nsew")
        self.btn_previous.grid(row=1, column=0, columnspan=1, padx=20, pady=(25, 50), sticky="we")
        self.lbl_index.grid(row=1, column=1, columnspan=1, padx=20, pady=(25, 50), sticky="nsew")
        self.btn_next.grid(row=1, column=2, columnspan=1, padx=20, pady=(25, 50), sticky="we")
    
    def new_canvas_toplevel(self, fig):
        self.canvas_toplevel.get_tk_widget().destroy()

        self.canvas_toplevel = FigureCanvasTkAgg(fig, master=self.beat_toplevel)
        self.canvas_toplevel.draw()
        self.canvas_toplevel.get_tk_widget().grid(row=0, column=0, columnspan=3, padx=50, pady=(50, 25), sticky="nsew")
    
    def load_other_results_button(self, results, event_handler):
        for button in self.other_result_btn:
            button.destroy()
        
        self.other_result_btn = []
        for result in results:
            btn = AnimatedButton(
                master=self.other_result_frame,
                text=f"{result.id} - Lead {get_lead_display_name(result.lead)}",
                font=("Bahnschrift", 14),
                fg_color="#2A2A2A",
                on_hover="#242424",
                height=40,
                transition_delay=100,
                command=lambda res=result: event_handler(res)
            )
            btn.pack(expand=True, fill="both", pady=5)

            self.other_result_btn.append(btn)
        

        