import json
import matplotlib.pyplot as plt

from models.detection_result_model import DetectionResult
from detection.detection import plot_all_detection, plot_jpoint_baseline
from detection import util_func

class ResultController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.frame = self.view.frames["result"]

        self.result: DetectionResult = None

        self.fig = None

        self._bind()

    def _bind(self):
        self.frame.if_btn_each_beat.configure(command=self.beat_toplevel_wrapper)
    
    def beat_toplevel_wrapper(self):
        self.frame.create_beat_toplevel()
        self.curr_figure_idx = 0

        self.denoised_beats = self.result.denoised_data
        self.delineations = self.result.delineation_result
        self.beat_interpretations = self.result.detection_result

        if not isinstance(self.result.denoised_data[0], list):
            self.denoised_beats = []
            self.delineations = []
            self.beat_interpretations = []
            for interpretation, beat_start_end in self.result.detection_result:
                start, end = beat_start_end

                self.denoised_beats.append(self.result.denoised_data[start:end])
                self.delineations.append(self.result.delineation_result[start:end])
                self.beat_interpretations.append(interpretation)

        self.frame.lbl_index.configure(text=f"{self.curr_figure_idx + 1} / {len(self.beat_interpretations)}")
        self.curr_figure = plot_jpoint_baseline(
            self.denoised_beats[self.curr_figure_idx],
            self.delineations[self.curr_figure_idx],
            self.beat_interpretations[self.curr_figure_idx],
            f"{self.result.dirname}_{self.curr_figure_idx + 1}"
        )
        self.frame.new_canvas_toplevel(
            self.curr_figure
        )

        self.frame.btn_previous.configure(command=self.previous_beat)
        self.frame.btn_next.configure(command=self.next_beat)
    
    def previous_beat(self):
        if self.curr_figure_idx == 0:
            return
        self.curr_figure_idx -= 1

        self.frame.lbl_index.configure(text=f"{self.curr_figure_idx + 1} / {len(self.beat_interpretations)}")

        plt.close(self.curr_figure)
        self.curr_figure = plot_jpoint_baseline(
            self.denoised_beats[self.curr_figure_idx],
            self.delineations[self.curr_figure_idx],
            self.beat_interpretations[self.curr_figure_idx],
            f"{self.result.dirname}_{self.curr_figure_idx + 1}"
        )
        self.frame.new_canvas_toplevel(
            self.curr_figure
        )

    def next_beat(self):
        if self.curr_figure_idx == len(self.beat_interpretations) - 1:
            return
        self.curr_figure_idx += 1

        self.frame.lbl_index.configure(text=f"{self.curr_figure_idx + 1} / {len(self.beat_interpretations)}")

        plt.close(self.curr_figure)
        self.curr_figure = plot_jpoint_baseline(
            self.denoised_beats[self.curr_figure_idx],
            self.delineations[self.curr_figure_idx],
            self.beat_interpretations[self.curr_figure_idx],
            f"{self.result.dirname}_{self.curr_figure_idx + 1}"
        )
        self.frame.new_canvas_toplevel(
            self.curr_figure
        )

    def load_result(self, detection_result: DetectionResult):
        self.result = detection_result

        self.other_results = DetectionResult.get_by_pasien(self.result.pasien)
        self.frame.load_other_results_button(self.other_results, self.other_result_btn_event_handler)

        if self.fig:
            plt.close(self.fig)

        self.fig = plot_all_detection(
            self.result.denoised_data,
            self.result.detection_result,
            self.result.dirname
        )
        
        self.curr_figure_idx = 0

        self.frame.new_canvas(self.fig)

        self.frame.if_lbl_1.configure(text=f"ID Pasien: {str(detection_result.pasien.id)}")
        self.frame.if_lbl_2.configure(text=f"ID Hasil: {str(detection_result.id)}")
        self.frame.if_lbl_3.configure(text=f"Nama Pasien: {detection_result.pasien.nama.title()}")
        self.frame.if_lbl_4.configure(text=f"Lead: {util_func.get_lead_display_name(detection_result.lead)}")
        
    def other_result_btn_event_handler(self, result):
        self.load_result(result)