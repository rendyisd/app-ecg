from .dashboard_controller import DashboardController
from .result_controller import ResultController
from .slide_panel_controller import SlidePanelController

class Controller:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view

        self.slide_panel_controller = SlidePanelController(model, view, self)
        self.dashboard_controller = DashboardController(model, view, self)
        self.result_controller = ResultController(model, view)

    def start(self):
        self.view.switch('dashboard')

        self.view.start_mainloop()