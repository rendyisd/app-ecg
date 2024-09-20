from .dashboard_controller import DashboardController
from .result_controller import ResultController

class Controller:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view

        self.result_controller = ResultController(model, view)
        self.dashboard_controller = DashboardController(model, view, self.result_controller)

    def start(self):
        self.view.switch('dashboard')

        self.view.start_mainloop()