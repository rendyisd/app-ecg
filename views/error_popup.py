import customtkinter

class ErrorPopup(customtkinter.CTkFrame):
    def __init__(self, master, message):
        super().__init__(master)
        
        self.configure(
            border_width=2,
            corner_radius=10,
            fg_color='red',
            border_color='red',
        )
        
        self.message_label = customtkinter.CTkLabel(
            self,
            text=message,
            text_color='white',
            font=("Helvetica", 12),
            fg_color='red'
        )
        self.message_label.pack(padx=10, pady=10)
        
        self.place(relx=0.5, rely=0.5, anchor="center")

        # destroy self after 2000 ms
        self.after(2000, self.dismiss)

    def dismiss(self):
        self.destroy()