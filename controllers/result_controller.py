import json

from models.detection_result_model import DetectionResult
from detection.detection import plot_all_detection, plot_jpoint_baseline

class ResultController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.frame = self.view.frames["result"]

        self.result: DetectionResult = None

        self._bind()

    def _bind(self):
        pass
    
    def load_result(self, detection_result: DetectionResult):
        self.result = detection_result

        fig = plot_all_detection(
            self.result.denoised_data,
            self.result.detection_result,
            self.result.dirname
        )
        
        self.frame.new_canvas(fig)