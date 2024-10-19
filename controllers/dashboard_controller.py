import os
import shutil
import json

from datetime import datetime
from tkinter import filedialog
from models.record_model import Record
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

        self.record_options_to_record = {}
        self.lead_options_to_lead = {
            "Lead I": ["i"],
            "Lead II": ["ii"],
            "Lead III": ["iii"],
            "Lead aVF": ["avf"],
            "Lead aVR": ["avr"],
            "Lead aVL": ["avl"],
            "Lead V1": ["v1"],
            "Lead V2": ["v2"],
            "Lead V3": ["v3"],
            "Lead V4": ["v4"],
            "Lead V5": ["v5"],
            "Lead V6": ["v6"],
            "Semua lead": ["i", "ii", "iii", "avf", "avr", "avl", "v1", "v2", "v3", "v4", "v5", "v6"]
        }

        self._bind()

    def _bind(self):
        self.view.root.btn_slide_panel.configure(command=self.view.root.main_slide_panel.animate)

        self.frame.btn_upload_file.configure(command=self.upload_file)
        self.frame.btn_dat_file.configure(command=self.unselect_dat_file)
        self.frame.btn_hea_file.configure(command=self.unselect_hea_file)

        self.frame.btn_start_detect.configure(command=self.start_detection)
    
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
    
    def _wrapper(self, record, lead):
        record_dir = os.path.join("bin", f"Record {record.name}")
        basename_format = f"Record {record.name} - Lead {util_func.get_lead_display_name(lead)}"

        result_root = os.path.join(record_dir, basename_format) # filepath

        util_func.make_dir(result_root)

        new_dat_path = os.path.join(record_dir, os.path.basename(self.selected_dat_path))
        new_hea_path = os.path.join(record_dir, os.path.basename(self.selected_hea_path))

        if not os.path.exists(new_dat_path):
            shutil.copy(self.selected_dat_path, new_dat_path)
            shutil.copy(self.selected_hea_path, new_hea_path)

        denoised_beats, delineations, beat_interpretations = detection(
            os.path.splitext(new_dat_path)[0],
            lead,
            result_root
        )

        detection_result = DetectionResult.create(
            record,
            lead,
            basename_format,
            denoised_beats,
            delineations,
            beat_interpretations
        )

        return detection_result


    def start_detection(self):
        lead_option = self.frame.dropdown_form_lead.get()
        
        if lead_option == "":
            _ = ErrorPopup(self.view.root, "Error: Tidak ada lead yang dipilih!")
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
        
        import wfdb

        r_name = wfdb.rdrecord(os.path.splitext(self.selected_dat_path)[0]).record_name
        record = Record.get_or_create(r_name)

        lead_choices = []
        lead_choices.extend(self.lead_options_to_lead[lead_option])

        # check if record + lead detection already exist or not, if already exist remove from leads
        record_leads = [res.lead for res in DetectionResult.get_by_record(record)]
        leads = [lead for lead in lead_choices if lead not in record_leads]

        detection_result = None

        for lead in leads:
            detection_result = self._wrapper(record, lead)
        
        if detection_result is None:
            # DetectionResult leads index 0
            detection_result = DetectionResult.get_by_record_lead(record, lead_choices[0])

        self.controller.result_controller.load_result(detection_result)
        self.controller.slide_panel_controller.load_records()

        self.view.switch('result')

