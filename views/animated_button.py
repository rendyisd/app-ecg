import customtkinter

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def interpolate_color(color1, color2, factor):
    return tuple(
        int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3)
    )

class AnimatedButton(customtkinter.CTkButton):
    def __init__(self, *args, on_hover, transition_delay, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_color = self.cget("fg_color")
        self.hover_color = on_hover

        self.steps = 15
        self.transition_delay = transition_delay
        self.curr_transition_step = 0

        self.is_on_hover = False
        self.animation_job = None

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event=None):
        if self.animation_job:
            self.after_cancel(self.animation_job)
        self.is_on_hover = True
        self.animate()

    def _on_leave(self, event=None):
        if self.animation_job:
            self.after_cancel(self.animation_job)
        self.is_on_hover = False
        self.animate()

    def animate(self):
        if (self.curr_transition_step == self.steps and self.is_on_hover) or (self.curr_transition_step == 0 and not self.is_on_hover):
            self.animation_job = None
            return

        factor = self.curr_transition_step / self.steps
        start_rgb = hex_to_rgb(self.default_color)
        end_rgb = hex_to_rgb(self.hover_color)
        new_color = rgb_to_hex(interpolate_color(start_rgb, end_rgb, factor))

        self.configure(fg_color=new_color)

        self.curr_transition_step += 1 if self.is_on_hover else -1

        self.animation_job = self.after(self.transition_delay // self.steps, self.animate)
        