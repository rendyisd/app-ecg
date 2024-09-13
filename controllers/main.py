from .dashboard_controller import DashboardController

class Controller:
    def __init__(self, model, view) -> None:
        self.model = model
        self.view = view

        self.dashboard_controller = DashboardController(model, view)

    def start(self):
        self.view.switch('dashboard')

        self.view.start_mainloop()