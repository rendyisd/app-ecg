import os
import shutil
import json

from datetime import datetime
from tkinter import filedialog
from models.pasien_model import Pasien
from models.detection_result_model import DetectionResult
from views.error_popup import ErrorPopup

from detection.detection import detection

from detection import util_func

class DashboardController:
    def __init__(self, model, view, controller):
        self.model = model
        self.view = view
        self.controller = controller

        self.frame = self.view.frames["dashboard"]

        self.selected_dat_path = None
        self.selected_hea_path = None

        self.pasien_options_to_pasien = {}
        self.lead_options_to_lead = {
            "Lead I": "i",
            "Lead II": "ii",
            "Lead III": "iii",
            "Lead aVF": "avf",
            "Lead aVR": "avr",
            "Lead aVL": "avl",
            "Lead V1": "v1",
            "Lead V2": "v2",
            "Lead V3": "v3",
            "Lead V4": "v4",
            "Lead V5": "v5",
            "Lead V6": "v6",
        }

        self._bind()
        self.load_pasien()

    def _bind(self):
        self.view.root.btn_slide_panel.configure(command=self.view.root.main_slide_panel.animate)

        self.frame.btn_add_pasien.configure(command=self.add_pasien_toplevel_wrapper)

        self.frame.btn_upload_file.configure(command=self.upload_file)
        self.frame.btn_dat_file.configure(command=self.unselect_dat_file)
        self.frame.btn_hea_file.configure(command=self.unselect_hea_file)

        self.frame.btn_start_detect.configure(command=self.start_detection)
    
    def load_pasien(self):
        self.pasien_options_to_pasien = {}

        all_pasien = Pasien.get_all()
        
        for pasien in all_pasien:
            option_str = f"{pasien.id} - {pasien.nama.title()}"
            self.pasien_options_to_pasien[option_str] = pasien
        
        self.frame.dropdown_form_pasien.configure(values=self.pasien_options_to_pasien.keys())

        if len(all_pasien) > 0:
            self.frame.dropdown_form_pasien.set(f"{all_pasien[0].id} - {all_pasien[0].nama.title()}")
        
        else:
            self.frame.dropdown_form_pasien.set("")


    def add_pasien_toplevel_wrapper(self):
        self.frame.create_add_pasien_toplevel()
        self.frame.btn_submit_add_pasien.configure(command=self.submit_add_pasien)

    def submit_add_pasien(self):
        entry_value = self.frame.entry_nama_pasien.get().strip().lower()

        valid, e_msg = Pasien.validate(entry_value)
        if not valid:
            e_msg = f"Error: {e_msg}"
            _ = ErrorPopup(self.frame.add_pasien_toplevel, e_msg)
            return

        self.model.pasien.create(entry_value)

        self.load_pasien()

        self.frame.destroy_add_pasien_toplevel()
    
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
                _ = ErrorPopup(self.view.root, "Error: File yang dipilih tidak valid!")
    
    def unselect_dat_file(self):
        if self.selected_dat_path:
            self.selected_dat_path = None
            self.frame.btn_dat_file.configure(text="Tidak ada file .dat yang dipilih")

    def unselect_hea_file(self):
        if self.selected_hea_path:
            self.selected_hea_path = None
            self.frame.btn_hea_file.configure(text="Tidak ada file .hea yang dipilih")

    def start_detection(self):
        pasien_option = self.frame.dropdown_form_pasien.get()
        lead_option = self.frame.dropdown_form_lead.get()

        if pasien_option == "":
            _ = ErrorPopup(self.view.root, "Error: Tidak ada pasien yang dipilih!")
            return
        
        elif lead_option == "":
            _ = ErrorPopup(self.view.root, "Error: Tidak ada pasien yang dipilih!")
            return
        
        elif not self.selected_dat_path:
            _ = ErrorPopup(self.view.root, "Error: Tidak ada file .dat yang dipilih!")
            return
        
        elif not self.selected_hea_path:
            _ = ErrorPopup(self.view.root, "Error: Tidak ada file .hea yang dipilih!")
            return
        
        elif os.path.splitext(os.path.basename(self.selected_dat_path))[0] !=\
            os.path.splitext(os.path.basename(self.selected_hea_path))[0]:
            _ = ErrorPopup(self.view.root, "Error: File .dat dan .hea yang dipilih tidak sama!")
            return
        
        pasien = self.pasien_options_to_pasien[self.frame.dropdown_form_pasien.get()]

        lead = self.lead_options_to_lead[lead_option]

        pasien_dir = os.path.join("bin", f"{pasien.id}_{pasien.nama}")
        basename_format = f"{pasien.id}_{pasien.nama}_{lead_option}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        result_root = os.path.join(pasien_dir, basename_format) # filepath
        result_dir = os.path.join(result_root, "result")

        util_func.make_dir(result_dir)

        new_dat_path = os.path.join(result_root, os.path.basename(self.selected_dat_path))
        new_hea_path = os.path.join(result_root, os.path.basename(self.selected_hea_path))

        shutil.copy(self.selected_dat_path, new_dat_path)
        shutil.copy(self.selected_hea_path, new_hea_path)

        denoised_beats, delineations, beat_interpretations = detection(os.path.splitext(new_dat_path)[0], lead, result_root)

        detection_result = DetectionResult.create(
            pasien,
            lead,
            basename_format,
            denoised_beats,
            delineations,
            beat_interpretations
        )

        self.controller.result_controller.load_result(detection_result)
        self.controller.slide_panel_controller.load_results()

        self.view.switch('result')

