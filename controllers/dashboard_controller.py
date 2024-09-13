from tkinter import filedialog

class DashboardController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.frame = self.view.frames["dashboard"]

        self.selected_dat_path = None
        self.selected_hea_path = None

        self._bind()

    def _bind(self):
        self.view.root.btn_slide_panel.configure(command=self.view.root.main_slide_panel.animate)

        self.frame.btn_add_pasien.configure(command=self.add_pasien_toplevel_wrapper)

        self.frame.btn_upload_file.configure(command=self.upload_file)
        self.frame.btn_dat_file.configure(command=self.unselect_dat_file)
        self.frame.btn_hea_file.configure(command=self.unselect_hea_file)

    def add_pasien_toplevel_wrapper(self):
        self.frame.create_add_pasien_toplevel()
        self.frame.btn_submit_add_pasien.configure(command=self.submit_add_pasien)

    def submit_add_pasien(self):
        # Validate
        entry_value = self.frame.entry_nama_pasien.get()
        print(entry_value)
        # self.frame.entry_nama_pasien
    
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DAT and HEA files", "*.dat *.hea")])

        if file_path:
            file_extension = file_path.split('.')[-1].lower()
            if file_extension == "dat":
                self.selected_dat_path = file_path
                self.frame.btn_dat_file.configure(text=f"{file_path.split('/')[-1]}")
            elif file_extension == "hea":
                self.selected_hea_path = file_path
                self.frame.btn_hea_file.configure(text=f"{file_path.split('/')[-1]}")
            else:
                print("Invalid file selected")
    
    def unselect_dat_file(self):
        if self.selected_dat_path:
            self.selected_dat_path = None
            self.frame.btn_dat_file.configure(text="Tidak ada file .dat yang dipilih")

    def unselect_hea_file(self):
        if self.selected_hea_path:
            self.selected_hea_path = None
            self.frame.btn_hea_file.configure(text="Tidak ada file .dat yang dipilih")
