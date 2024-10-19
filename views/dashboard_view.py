import tkinter
import customtkinter

from .animated_button import AnimatedButton

class DashboardView(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_record_toplevel = None

        self.grid_rowconfigure(0, weight=1) # Padding
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1) 
        self.grid_rowconfigure(7, weight=1) # Padding

        self.columnconfigure(0, weight=1, uniform="uniform") # Padding
        self.columnconfigure(1, weight=1, uniform="uniform")
        self.columnconfigure(2, weight=1, uniform="uniform")
        self.columnconfigure(3, weight=1, uniform="uniform") # Padding

        self._font_form_fieldname = customtkinter.CTkFont(
            family="Bahnschrift",
            size=16,
            weight="bold"
        )
        self._font_form_sub = customtkinter.CTkFont(
            family="Bahnschrift",
            size=10
        )

        self.lbl_title = customtkinter.CTkLabel(
            self,
            font=('Bahnschrift', 24, 'bold'),
            text="DELINEASI DAN DETEKSI\nELEVASI DAN DEPRESI SEGMEN ST",
        )

        self.lbl_form_upload = customtkinter.CTkLabel(
            self,
            font=self._font_form_fieldname,
            text="Upload File"
        )

        self.lbl_upload_sub = customtkinter.CTkLabel(
            self,
            font=self._font_form_sub,
            text="Keterangan: Diperlukan dua file, (.dat) dan (.hea) dengan nama yang sama.",
            text_color="#999999",
            height=20
        )

        self.dropdown_form_lead = customtkinter.CTkOptionMenu(
            self,
            values=["Lead I", "Lead II", "Lead III", "Lead aVF", "Lead aVR", "Lead aVL", "Lead V1", "Lead V2", "Lead V3", "Lead V4", "Lead V5", "Lead V6", "Semua lead"],
        )

        self.btn_upload_file = AnimatedButton(
            master=self,
            text="Upload File",
            font=self._font_form_fieldname,
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )
        
        self.btn_dat_file = AnimatedButton(
            master=self,
            text="Tidak ada file .dat yang dipilih",
            font=self._font_form_fieldname,
            fg_color="#E53935",
            on_hover="#B71C1C",
            transition_delay=100,
            width=400
        )

        self.btn_hea_file = AnimatedButton(
            master=self,
            text="Tidak ada file .hea yang dipilih",
            font=self._font_form_fieldname,
            fg_color="#E53935",
            on_hover="#B71C1C",
            transition_delay=100,
            width=400
        )

        self.btn_start_detect = AnimatedButton(
            master=self,
            text="Mulai Deteksi",
            font=self._font_form_fieldname,
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )

        self.lbl_title.grid(row=1, column=1, columnspan=2, sticky="nsew")

        self.lbl_form_upload.grid(row=2, column=1, columnspan=2, sticky="w")
        self.lbl_upload_sub.grid(row=2, column=1, columnspan=2, sticky="sw")

        self.dropdown_form_lead.grid(row=3, column=1, padx=(0, 5), sticky="new")
        self.btn_upload_file.grid(row=3, column=2, padx=(5, 0), sticky="new")
    
        self.btn_dat_file.grid(row=4, column=1, columnspan=2, pady=(0, 10), sticky="nsew")
        self.btn_hea_file.grid(row=5, column=1, columnspan=2, pady=(10, 0), sticky="nsew")

        self.btn_start_detect.grid(row=6, column=1, columnspan=2, pady=10, sticky="s")