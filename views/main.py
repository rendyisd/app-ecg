from .root import Root

from .dashboard_view import DashboardView

class View:
    def __init__(self):
        self.root = Root()

        self.frames = {}

        self.current_frame = None

        self._add_frame(DashboardView, 'dashboard')

    def _add_frame(self, Frame, name):
        self.frames[name] = Frame(self.root, fg_color="transparent")
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    def switch(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()

        self.root.main_slide_panel.tkraise() # The main slide panel should always be on top
        self.root.btn_slide_panel.tkraise()
        
        self.current_frame = frame
        self.current_frame.grid(row=0, column=0, sticky="nsew")
    
    def start_mainloop(self):
        self.root.mainloop()