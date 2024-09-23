import shutil
import os

from models.pasien_model import Pasien
from models.detection_result_model import DetectionResult

from detection.util_func import get_lead_display_name
from views.error_popup import ErrorPopup

class SlidePanelController:
    def __init__(self, model, view, controller):
        self.model = model
        self.view = view

        self.controller = controller

        self.pasien_options_to_pasien = {}
        self.result_options_to_result = {}

        self.frame = self.view.root.main_slide_panel
    
        self._bind()
        self.load_results()
    
    def _bind(self):
        self.frame.btn_dashboard.configure(command=self.switch_to_dashboard)
        self.frame.btn_hapus.configure(command=self.hapus_toplevel_wrapper)
    
    def switch_to_dashboard(self):
        self.view.switch("dashboard")
    
    def hapus_toplevel_wrapper(self):
        self.frame.create_hapus_toplevel()

        self.active_btn = "pasien"
        self.choose_hapus_pasien() # set default active state

        self.frame.btn_pasien.configure(command=self.choose_hapus_pasien)
        self.frame.btn_result.configure(command=self.choose_hapus_result)
        self.frame.btn_submit_hapus.configure(command=self.submit_hapus)
    
    def load_results(self):
        for btn in self.frame.all_result_btn:
            btn.destroy()

        all_pasien = Pasien.get_all()

        for pasien in all_pasien:
            pasien_results = DetectionResult.get_by_pasien(pasien)

            for result in pasien_results:
                pasien_name = Pasien.get_by_id(result.pasien.id).nama.title()

                self.frame.load_result_button(result, pasien_name, self.load_result_btn_event_handler)

    def load_result_btn_event_handler(self, result):
        self.controller.result_controller.load_result(result)
        self.view.switch("result")

    def choose_hapus_pasien(self):
        self.pasien_options_to_pasien = {}
        state = {
            "active": ["#007BFF", "#E53935"],
            "inactive": ["#E53935", "#007BFF"]
        }

        if self.active_btn == "result":
            self.frame.btn_result.configure(fg_color=state["inactive"])

        self.active_btn = "pasien"
        self.frame.btn_pasien.configure(fg_color=state["active"])

        all_pasien = Pasien.get_all()
        
        for pasien in all_pasien:
            option_str = f"{pasien.id} - {pasien.nama.title()}"
            self.pasien_options_to_pasien[option_str] = pasien
        
        self.frame.dropdown_items.configure(values=self.pasien_options_to_pasien.keys())

        if len(self.pasien_options_to_pasien) > 0:
            self.frame.dropdown_items.set(f"{list(self.pasien_options_to_pasien.keys())[0]}")
        
        else:
            self.frame.dropdown_items.set("")

    def choose_hapus_result(self):
        self.result_options_to_result = {}
        state = {
            "active": ["#007BFF", "#E53935"],
            "inactive": ["#E53935", "#007BFF"]
        }

        if self.active_btn == "pasien":
            self.frame.btn_pasien.configure(fg_color=state["inactive"])

        self.active_btn = "result"
        self.frame.btn_result.configure(fg_color=state["active"])

        all_pasien = Pasien.get_all()

        for pasien in all_pasien:
            pasien_results = DetectionResult.get_by_pasien(pasien)

            for result in pasien_results:
                pasien_name = Pasien.get_by_id(result.pasien.id).nama.title()

                option_str = f"{pasien_name} - {result.id} - Lead {get_lead_display_name(result.lead)}"
                self.result_options_to_result[option_str] = result
            
        self.frame.dropdown_items.configure(values=self.result_options_to_result.keys())

        if len(self.result_options_to_result) > 0:
            self.frame.dropdown_items.set(f"{list(self.result_options_to_result.keys())[0]}")
        
        else:
            self.frame.dropdown_items.set("")
    
    def submit_hapus(self):
        option = self.frame.dropdown_items.get()

        if option == "":
            _ = ErrorPopup(self.frame.hapus_toplevel, "Error: Tidak ada opsi yang dipilih!")
            return

        if self.active_btn == "pasien":
            pasien_to_delete = self.pasien_options_to_pasien[option]

            pasien_results = DetectionResult.get_by_pasien(pasien_to_delete)

            # delete pasien results
            for result in pasien_results:
                result.delete()
            
            pasien_dir = os.path.join("bin", f"{pasien_to_delete.id}_{pasien_to_delete.nama}")

            if os.path.exists(pasien_dir):
                shutil.rmtree(pasien_dir)
            else:
                print("Directory does not exist.")

            pasien_to_delete.delete()

        elif self.active_btn == "result":
            result_to_delete = self.result_options_to_result[option]

            result_dir = os.path.join("bin", f"{result_to_delete.pasien.id}_{result_to_delete.pasien.nama}", result_to_delete.dirname)

            if os.path.exists(result_dir):
                shutil.rmtree(result_dir)
            else:
                print("Directory does not exist.")

            result_to_delete.delete()
        
        # reload
        self.controller.dashboard_controller.load_pasien()
        self.load_results()
        self.view.switch("dashboard") # i dont know how to reload result_view if the current laoded result is deleted so just load dashboard lol

        self.frame.destroy_hapus_toplevel()