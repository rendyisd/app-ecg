import tkinter
import customtkinter

from .animated_button import AnimatedButton

class DashboardView(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_pasien_toplevel = None

        self.grid_rowconfigure(0, weight=1) # Padding
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1) # Padding

        self.columnconfigure(0, weight=1, uniform="uniform") # Padding
        self.columnconfigure(1, weight=2, uniform="uniform")
        self.columnconfigure(2, weight=2, uniform="uniform")
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
            text="DETEKSI ELEVASI DAN DEPRESI SEGMEN ST",
        )

        self.lbl_form_pasien = customtkinter.CTkLabel(
            self,
            font=self._font_form_fieldname,
            text="Data Pasien",
        )

        self.lbl_pasien_sub = customtkinter.CTkLabel(
            self,
            font=self._font_form_sub,
            text="Keterangan: Tambahkan pasien terlebih dahulu baru bisa dipilih.",
            text_color="#999999",
            height=20
        )

        self.dropdown_form_pasien = customtkinter.CTkOptionMenu(
            self,
            values=[""]
        )

        self.btn_add_pasien = AnimatedButton(
            master=self,
            text="Tambahkan Pasien",
            font=self._font_form_fieldname,
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
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
            values=["Lead I", "Lead II", "Lead III", "Lead aVF", "Lead aVR", "Lead aVL", "Lead V1", "Lead V2", "Lead V3", "Lead V4", "Lead V5", "Lead V6"],
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

        self.lbl_form_pasien.grid(row=2, column=1, columnspan=2, sticky="w")
        self.lbl_pasien_sub.grid(row=2, column=1, columnspan=2, sticky="sw")

        self.dropdown_form_pasien.grid(row=3, column=1, columnspan=1, sticky="new")
        self.btn_add_pasien.grid(row=3, column=2, columnspan=1, padx=(10, 0), sticky="new")

        self.lbl_form_upload.grid(row=4, column=1, columnspan=2, sticky="w")
        self.lbl_upload_sub.grid(row=4, column=1, columnspan=2, sticky="sw")

        self.dropdown_form_lead.grid(row=5, column=1, columnspan=1, sticky="new")
        self.btn_upload_file.grid(row=5, column=2, columnspan=1, padx=(10, 0), sticky="new")
    
        self.btn_dat_file.grid(row=6, column=1, padx=(0, 5), sticky="ns")
        self.btn_hea_file.grid(row=6, column=2, padx=(5, 0), sticky="ns")

        self.btn_start_detect.grid(row=7, column=1, pady=10, columnspan=1, sticky="s")
        
        self.btn_test = AnimatedButton(
            master=self,
            text="Testing",
            font=self._font_form_fieldname,
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )
        self.btn_test.grid(row=7, column=2, pady=10, columnspan=1, sticky="s")

    def create_add_pasien_toplevel(self):
        self.add_pasien_toplevel = customtkinter.CTkToplevel(self)
        self.add_pasien_toplevel.title("Tambahkan Pasien")
        self.add_pasien_toplevel.geometry(f"{550}x{290}")
        self.add_pasien_toplevel.resizable(False, False)
        self.add_pasien_toplevel.grab_set()

        self.center_frame = customtkinter.CTkFrame(self.add_pasien_toplevel)
        self.center_frame.pack(expand=True)

        self.lbl_nama_pasien = customtkinter.CTkLabel(self.center_frame, text="Nama Pasien", font=self._font_form_fieldname)
        self.entry_nama_pasien = customtkinter.CTkEntry(self.center_frame, placeholder_text="Masukkan nama pasien", width=300)
        self.btn_submit_add_pasien = AnimatedButton(
            master=self.center_frame,
            text="Submit",
            font=self._font_form_fieldname,
            fg_color="#007BFF",
            on_hover="#0056B3",
            transition_delay=100
        )

        self.lbl_nama_pasien.pack(anchor="center", pady=(10, 5), padx=10)
        self.entry_nama_pasien.pack(anchor="center", pady=10, padx=10)
        self.btn_submit_add_pasien.pack(anchor="center", pady=(10, 20), padx=10)
    
    def destroy_add_pasien_toplevel(self):
        if self.add_pasien_toplevel is not None:
            self.add_pasien_toplevel.destroy()
            self.add_pasien_toplevel = None