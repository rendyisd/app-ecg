import customtkinter

from .animated_button import AnimatedButton
from detection.util_func import get_lead_display_name

class SlidePanel(customtkinter.CTkFrame):
    def __init__(self, master, start_pos, end_pos):
        super().__init__(master=master, corner_radius=0)

        self.all_result_btn = []
        self.hapus_toplevel = None

        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = abs(self.start_pos - self.end_pos)

        self.curr_pos = self.start_pos
        self.in_start_pos = True

        self.grid_rowconfigure(0, weight=0, minsize=80)  # small indentation for button
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0, minsize=80) # delete button???

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        top_label = customtkinter.CTkLabel(self, text="Top Row", fg_color="transparent")

        # bottom_label = customtkinter.CTkLabel(self, text="Bottom Row", fg_color="#333333")
        # bottom_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.frame_results = customtkinter.CTkScrollableFrame(
            self,
            fg_color="#333333"
        )

        self.btn_dashboard = AnimatedButton(
            master=self,
            text="Tambahkan",
            font=("Bahnschrift", 16, "bold"),
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )

        self.btn_hapus = AnimatedButton(
            master=self,
            text="Hapus",
            font=("Bahnschrift", 16, "bold"),
            fg_color="#E53935",
            on_hover="#B71C1C",
            transition_delay=100
        )

        self.frame_results.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        self.btn_dashboard.grid(row=2, column=0, columnspan=1, sticky="nsew", padx=10, pady=(0, 10))
        self.btn_hapus.grid(row=2, column=1, columnspan=1, sticky="nsew", padx=10, pady=(0, 10))

        self.place(relx=self.start_pos, rely=0, relwidth=self.width, relheight=1)

    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backward()

    def animate_forward(self):
        if self.curr_pos < self.end_pos:
            self.curr_pos = (self.curr_pos + 0.008) if self.curr_pos + 0.008 < self.end_pos else self.end_pos
            self.place(relx = self.curr_pos, rely = 0, relwidth = self.width, relheight = 1)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False

    def animate_backward(self):
        if self.curr_pos > self.start_pos:
            self.curr_pos = (self.curr_pos - 0.008) if self.curr_pos - 0.008 > self.start_pos else self.start_pos
            self.place(relx = self.curr_pos, rely = 0, relwidth = self.width, relheight = 1)
            self.after(10, self.animate_backward)
        else:
            self.in_start_pos = True
    
    def load_result_button(self, result, pasien_name, event_handler):
        btn = AnimatedButton(
            master=self.frame_results,
            text=f"{pasien_name}\n{result.id} - Lead {get_lead_display_name(result.lead)}",
            font=("Bahnschrift", 12),
            fg_color="#2A2A2A",
            on_hover="#242424",
            height=50,
            transition_delay=100,
            command=lambda res=result: event_handler(res)
        )
        
        btn.pack(expand=True, fill="both", pady=5)

        self.all_result_btn.append(btn)
    
    def create_hapus_toplevel(self):
        self.hapus_toplevel = customtkinter.CTkToplevel(self)
        self.hapus_toplevel.title("Hapus")
        self.hapus_toplevel.geometry(f"{550}x{290}")
        self.hapus_toplevel.resizable(False, False)
        self.hapus_toplevel.grab_set()

        self.center_frame = customtkinter.CTkFrame(self.hapus_toplevel)
        self.center_frame.pack(expand=True)

        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_rowconfigure(1, weight=1)
        self.center_frame.grid_rowconfigure(2, weight=1)

        self.center_frame.grid_columnconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(1, weight=2)

        self.btn_pasien = customtkinter.CTkButton(
            self.center_frame,
            text="Pasien",
            fg_color=["#E53935", "#007BFF"],
            font=("Bahnschrift", 12, "bold"),
        )
        self.btn_result = customtkinter.CTkButton(
            self.center_frame,
            text="Hasil Deteksi",
            fg_color=["#E53935", "#007BFF"],
            font=("Bahnschrift", 12, "bold"),
        )

        self.dropdown_items = customtkinter.CTkOptionMenu(
            self.center_frame,
            values=[""]
        )

        self.btn_submit_hapus = AnimatedButton(
            master=self.center_frame,
            text="Hapus",
            font=("Bahnschrift", 16, "bold"),
            fg_color="#E53935",
            on_hover="#B71C1C",
            transition_delay=100
        )

        self.btn_pasien.grid(row=0, column=0, columnspan=1, padx=5, pady=5)
        self.btn_result.grid(row=0, column=1, columnspan=1, padx=5, pady=5)
        self.dropdown_items.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.btn_submit_hapus.grid(row=2, column=0, columnspan=2)
    
    def destroy_hapus_toplevel(self):
        if self.hapus_toplevel is not None:
            self.hapus_toplevel.destroy()
            self.hapus_toplevel = None