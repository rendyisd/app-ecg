import customtkinter

class SlidePanel(customtkinter.CTkFrame):
    def __init__(self, master, start_pos, end_pos):
        super().__init__(master=master, corner_radius=0)

        self.start_pos = start_pos
        self.end_pos = end_pos
        self.width = abs(self.start_pos - self.end_pos)

        self.curr_pos = self.start_pos
        self.in_start_pos = True

        self.grid_rowconfigure(0, weight=0, minsize=80)  # small indentation for button
        self.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=1)

        top_label = customtkinter.CTkLabel(self, text="Top Row", fg_color="transparent")
        top_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        bottom_label = customtkinter.CTkLabel(self, text="Bottom Row", fg_color="lightgreen")
        bottom_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.place(relx=self.start_pos, rely=0, relwidth=self.width, relheight=1)

    def animate(self):
        if self.in_start_pos:
            self.animate_forward()
        else:
            self.animate_backward()

    def animate_forward(self):
        if self.curr_pos < self.end_pos:
            self.curr_pos = (self.curr_pos + 0.008) if self.curr_pos + 0.008 < self.end_pos else self.end_pos
            self.place(relx = self.curr_pos, rely = 0, relwidth = self.width, relheight = 1)
            self.after(10, self.animate_forward)
        else:
            self.in_start_pos = False

    def animate_backward(self):
        if self.curr_pos > self.start_pos:
            self.curr_pos = (self.curr_pos - 0.008) if self.curr_pos - 0.008 > self.start_pos else self.start_pos
            self.place(relx = self.curr_pos, rely = 0, relwidth = self.width, relheight = 1)
            self.after(10, self.animate_backward)
        else:
            self.in_start_pos = True