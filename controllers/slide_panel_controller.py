import shutil
import os

from models.record_model import Record
from models.detection_result_model import DetectionResult

from detection.util_func import get_lead_display_name
from views.error_popup import ErrorPopup

class SlidePanelController:
    def __init__(self, model, view, controller):
        self.model = model
        self.view = view

        self.controller = controller

        self.record_options_to_record = {}
        self.result_options_to_result = {}

        self.frame = self.view.root.main_slide_panel
    
        self._bind()
        self.load_records()
    
    def _bind(self):
        self.frame.btn_dashboard.configure(command=self.switch_to_dashboard)
        self.frame.btn_hapus.configure(command=self.hapus_toplevel_wrapper)
    
    def switch_to_dashboard(self):
        self.view.switch("dashboard")
    
    def hapus_toplevel_wrapper(self):
        self.frame.create_hapus_toplevel()

        self.active_btn = "record"
        self.choose_hapus_record() # set default active state

        self.frame.btn_record.configure(command=self.choose_hapus_record)
        self.frame.btn_result.configure(command=self.choose_hapus_result)
        self.frame.btn_submit_hapus.configure(command=self.submit_hapus)
    
    def load_records(self):
        for btn in self.frame.all_result_btn:
            btn.destroy()

        all_record = Record.get_all()

        for record in all_record:
            record_results = DetectionResult.get_by_record(record)

            # Take the first DetectionResult of the record
            result = record_results[0]
            record_name = Record.get_by_id(result.record.id).name

            self.frame.load_record_button(result, record_name, self.load_result_btn_event_handler)

    def load_result_btn_event_handler(self, result):
        self.controller.result_controller.load_result(result)
        self.view.switch("result")

    def choose_hapus_record(self):
        self.record_options_to_record = {}
        state = {
            "active": ["#007BFF", "#E53935"],
            "inactive": ["#E53935", "#007BFF"]
        }

        if self.active_btn == "result":
            self.frame.btn_result.configure(fg_color=state["inactive"])

        self.active_btn = "record"
        self.frame.btn_record.configure(fg_color=state["active"])

        all_record = Record.get_all()
        
        for record in all_record:
            option_str = f"Record {record.name}"
            self.record_options_to_record[option_str] = record
        
        self.frame.dropdown_items.configure(values=self.record_options_to_record.keys())

        if len(self.record_options_to_record) > 0:
            self.frame.dropdown_items.set(f"{list(self.record_options_to_record.keys())[0]}")
        
        else:
            self.frame.dropdown_items.set("")

    def choose_hapus_result(self):
        self.result_options_to_result = {}
        state = {
            "active": ["#007BFF", "#E53935"],
            "inactive": ["#E53935", "#007BFF"]
        }

        if self.active_btn == "record":
            self.frame.btn_record.configure(fg_color=state["inactive"])

        self.active_btn = "result"
        self.frame.btn_result.configure(fg_color=state["active"])

        all_record = Record.get_all()

        for record in all_record:
            record_results = DetectionResult.get_by_record(record)

            for result in record_results:
                record_name = Record.get_by_id(result.record.id).name

                option_str = f"Record {record_name} - Lead {get_lead_display_name(result.lead)}"
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

        if self.active_btn == "record":
            record_to_delete = self.record_options_to_record[option]

            record_results = DetectionResult.get_by_record(record_to_delete)

            # delete record results
            for result in record_results:
                result.delete()
            
            record_dir = os.path.join("bin", f"Record {record_to_delete.name}")

            if os.path.exists(record_dir):
                shutil.rmtree(record_dir)
            else:
                print("Directory does not exist.")

            record_to_delete.delete()

        elif self.active_btn == "result":
            result_to_delete = self.result_options_to_result[option]

            result_dir = os.path.join("bin", f"Record {result_to_delete.record.name}", result_to_delete.dirname)

            if os.path.exists(result_dir):
                shutil.rmtree(result_dir)
            else:
                print("Directory does not exist.")

            result_to_delete.delete()

            # check if record is deleted or not
            temp_record = Record.get_by_id(result_to_delete.record.id)

            if not temp_record:
                shutil.rmtree(os.path.join("bin", f"Record {result_to_delete.record.name}"))
        
        # reload
        self.load_records()
        self.view.switch("dashboard") # i dont know how to reload result_view if the current laoded result is deleted so just load dashboard lol

        self.frame.destroy_hapus_toplevel()