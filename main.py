import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
from datetime import datetime

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, bg='#003300', fg='#000000', 
                 font=("Segoe UI", 12), width=100, height=40, corner_radius=15, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent.cget('bg'), 
                        highlightthickness=0, **kwargs)
        
        self.original_width = width
        self.original_height = height
        self.original_bg = bg
        self.command = command
        
        # Create rounded rectangle
        self.rect_id = self.create_rounded_rect(0, 0, width, height, corner_radius, fill=bg, outline=bg)
        
        # Add text
        self.text_id = self.create_text(width/2, height/2, text=text, fill=fg, font=font)
        
        # Bind events - simplified
        self.bind('<Button-1>', lambda e: command())
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
        self.bg = bg
        self.fg = fg
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def on_enter(self, e):
        """Simple hover effect - just change to gray"""
        self.itemconfig(self.rect_id, fill='#cccccc', outline='#cccccc')
        
    def on_leave(self, e):
        """Simple leave effect - restore original color"""
        self.itemconfig(self.rect_id, fill=self.bg, outline=self.bg)
        
    def brighten_color(self, color, factor):
        """Brighten color for hover effect"""
        if color.startswith('#'):
            rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            brighter_rgb = tuple(min(255, int(c * factor)) for c in rgb)
            return f'#{brighter_rgb[0]:02x}{brighter_rgb[1]:02x}{brighter_rgb[2]:02x}'
        return color

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg='#ffffff', corner_radius=15, **kwargs):
        super().__init__(parent, bg=parent.cget('bg'), highlightthickness=0, **kwargs)
        self.bg = bg
        self.corner_radius = corner_radius
        
    def create_rounded_bg(self, width, height):
        self.create_rounded_rect(0, 0, width, height, self.corner_radius, fill=self.bg, outline=self.bg)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

class ChoiceTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Choice Timer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#e8f5e8')  # Cute light green background
        
        # Timer variables
        self.time_left = 0
        self.timer_running = False
        self.timer_thread = None
        
        # Choice tracking
        self.choices = []
        self.current_choice = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main title
        title_frame = tk.Frame(self.root, bg='#e8f5e8')
        title_frame.pack(pady=30)
        
        title_label = tk.Label(title_frame, text="Choice Timer", font=("Segoe UI", 32, "bold"), 
                              bg='#e8f5e8', fg='#2d5a2d')
        title_label.pack()
        
        # Main content frame with two columns
        main_frame = tk.Frame(self.root, bg='#e8f5e8')
        main_frame.pack(fill='both', expand=True, padx=25)
        
        # Left column - Timer and Choices
        left_column = tk.Frame(main_frame, bg='#e8f5e8')
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        # Timer section with rounded corners
        timer_container = tk.Frame(left_column, bg='#e8f5e8')
        timer_container.pack(pady=20, fill='x', padx=10)
        
        timer_frame = RoundedFrame(timer_container, bg='#f0f9f0', corner_radius=35)  # More rounded
        timer_frame.pack(fill='x')
        timer_frame.create_rounded_bg(500, 200)
        
        timer_title = tk.Label(timer_frame, text="Timer", bg='#f0f9f0', 
                              font=("Segoe UI", 18, "bold"), fg='#2d5a2d')
        timer_title.pack(pady=(20, 10))
        
        self.time_label = tk.Label(timer_frame, text="00:00", font=("Segoe UI", 48, "bold"), 
                                  bg='#f0f9f0', fg='#7fb069')
        self.time_label.pack(pady=15)
        
        # Timer controls
        controls_frame = tk.Frame(timer_frame, bg='#f0f9f0')
        controls_frame.pack(pady=20)
        
        self.start_btn = RoundedButton(controls_frame, text="Start", command=self.start_timer,
                                      bg='#7fb069', fg='white', font=("Segoe UI", 12, "bold"), 
                                      width=100, height=35, corner_radius=25)  # More rounded
        self.start_btn.pack(side='left', padx=8)
        
        self.stop_btn = RoundedButton(controls_frame, text="Stop", command=self.stop_timer,
                                     bg='#8fbc8f', fg='white', font=("Segoe UI", 12, "bold"), 
                                     width=100, height=35, corner_radius=25)  # More rounded
        self.stop_btn.pack(side='left', padx=8)
        
        self.reset_btn = RoundedButton(controls_frame, text="Reset", command=self.reset_timer,
                                      bg='#9dc183', fg='white', font=("Segoe UI", 12, "bold"), 
                                      width=100, height=35, corner_radius=25)  # More rounded
        self.reset_btn.pack(side='left', padx=8)
        
        # Time input
        time_input_frame = tk.Frame(timer_frame, bg='#f0f9f0')
        time_input_frame.pack(pady=20)
        
        tk.Label(time_input_frame, text="Set time (seconds):", bg='#f0f9f0', 
                font=("Segoe UI", 12), fg='#2d5a2d').pack(side='left')
        self.time_entry = tk.Entry(time_input_frame, width=12, font=("Segoe UI", 14), 
                                  relief='solid', bd=1)
        self.time_entry.pack(side='left', padx=15)
        self.time_entry.insert(0, "60")
        
        # Choice section with rounded corners
        choice_container = tk.Frame(left_column, bg='#e8f5e8')
        choice_container.pack(pady=20, fill='x', padx=10)
        
        choice_frame = RoundedFrame(choice_container, bg='#f0f9f0', corner_radius=35)  # More rounded
        choice_frame.pack(fill='x')
        choice_frame.create_rounded_bg(500, 200)  # Increased height to fit input better
        
        choice_title = tk.Label(choice_frame, text="Make your choice", bg='#f0f9f0', 
                               font=("Segoe UI", 18, "bold"), fg='#2d5a2d')
        choice_title.pack(pady=(20, 20))
        
        # ABCD buttons with rounded corners
        choices_frame = tk.Frame(choice_frame, bg='#f0f9f0')
        choices_frame.pack(pady=20)
        
        self.choice_buttons = {}
        choice_colors = {'A': '#7fb069', 'B': '#8fbc8f', 'C': '#9dc183', 'D': '#a8d5a8'}
        
        for choice in ['A', 'B', 'C', 'D']:
            btn = RoundedButton(choices_frame, text=choice, command=lambda c=choice: self.make_choice(c),
                               bg=choice_colors[choice], fg='white', font=("Segoe UI", 20, "bold"),
                               width=90, height=65, corner_radius=40)  # Much more rounded
            btn.pack(side='left', padx=12)
            self.choice_buttons[choice] = btn
        
        # Right column - History
        right_column = tk.Frame(main_frame, bg='#e8f5e8')
        right_column.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        # History section with rounded corners
        history_container = tk.Frame(right_column, bg='#e8f5e8')
        history_container.pack(fill='both', expand=True, padx=10)
        
        history_frame = RoundedFrame(history_container, bg='#f0f9f0', corner_radius=35)  # More rounded
        history_frame.pack(fill='both', expand=True)
        history_frame.create_rounded_bg(400, 500)
        
        history_title = tk.Label(history_frame, text="Choice History", bg='#f0f9f0', 
                                font=("Segoe UI", 18, "bold"), fg='#2d5a2d')
        history_title.pack(pady=(20, 15))
        
        # LAP and Export buttons on separate lines
        button_frame = tk.Frame(history_frame, bg='#f0f9f0')
        button_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        # LAP button on first line
        lap_btn = RoundedButton(button_frame, text="LAP", command=self.add_lap_separator,
                                bg='#9dc183', fg='white', font=("Segoe UI", 11, "bold"), 
                                width=70, height=30, corner_radius=20)  # More rounded
        lap_btn.pack(side='right')
        
        # Export button on second line
        export_frame = tk.Frame(history_frame, bg='#f0f9f0')
        export_frame.pack(fill='x', padx=20, pady=(0, 15))
        
        export_btn = RoundedButton(export_frame, text="Export", command=self.export_answers,
                                  bg='#7fb069', fg='white', font=("Segoe UI", 11, "bold"), 
                                  width=90, height=30, corner_radius=20)  # More rounded
        export_btn.pack(side='right')
        
        # Choice listbox with scrollbar
        listbox_frame = tk.Frame(history_frame, bg='#f0f9f0')
        listbox_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.choice_listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 11), bg='#e8f5e8', 
                                        fg='#2d5a2d', selectmode='none', relief='flat', bd=0)
        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical', command=self.choice_listbox.yview)
        self.choice_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.choice_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Clear history button
        clear_btn = RoundedButton(history_frame, text="Clear", command=self.clear_history,
                                 bg='#b8d4b8', fg='white', font=("Segoe UI", 11, "bold"), 
                                 width=100, height=30, corner_radius=20)  # More rounded
        clear_btn.pack(pady=20)
        
    def export_answers(self):
        if not self.choices:
            messagebox.showinfo("Info", "No choices to export!")
            return
            
        # Extract just the choices without "Choice:" prefix
        clean_choices = []
        for choice_text in self.choices:
            # Since we removed "Choice:", just extract the choice letter directly
            if "] " in choice_text:
                # Get everything after "] "
                choice_part = choice_text.split("] ")[-1].strip()
                clean_choices.append(choice_part)
            # Keep LAP separators in export
            elif choice_text.startswith("_"):
                clean_choices.append(choice_text)
        
        # Create the export text - just the letters, no prefixes
        export_text = "My Choices:\n" + "\n".join(clean_choices)
        
        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Choices"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_text)
                messagebox.showinfo("Success", f"Choices exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def add_lap_separator(self):
        """Add a LAP separator line to the choice history"""
        separator_text = "________________"
        self.choices.append(separator_text)
        self.choice_listbox.insert(tk.END, separator_text)
        self.choice_listbox.see(tk.END)
        
        # Make the separator text stand out with different styling
        last_index = self.choice_listbox.size() - 1
        self.choice_listbox.itemconfig(last_index, fg='#7fb069', font=("Segoe UI", 11, "bold"))
        
    def start_timer(self):
        if not self.timer_running:
            try:
                self.time_left = int(self.time_entry.get())
                if self.time_left <= 0:
                    messagebox.showerror("Error", "Please enter a valid time!")
                    return
                    
                self.timer_running = True
                self.start_btn.config(state='disabled')
                
                self.timer_thread = threading.Thread(target=self.timer_countdown)
                self.timer_thread.daemon = True
                self.timer_thread.start()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number!")
    
    def timer_countdown(self):
        while self.time_left > 0 and self.timer_running:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            time_str = f"{minutes:02d}:{seconds:02d}"
            
            self.root.after(0, lambda: self.time_label.config(text=time_str))
            time.sleep(1)
            self.time_left -= 1
        
        if self.time_left <= 0:
            self.root.after(0, self.timer_finished)
    
    def timer_finished(self):
        self.timer_running = False
        self.start_btn.config(state='normal')
        self.time_label.config(text="00:00")
    
    def stop_timer(self):
        self.timer_running = False
        self.start_btn.config(state='normal')
    
    def reset_timer(self):
        self.stop_timer()
        self.time_left = 0
        self.time_label.config(text="00:00")
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "60")
    
    def make_choice(self, choice):
        timestamp = datetime.now().strftime("%H:%M:%S")
        choice_text = f"[{timestamp}] {choice}"  # Remove "Choice:" completely
        self.choices.append(choice_text)
        self.choice_listbox.insert(tk.END, choice_text)
        self.choice_listbox.see(tk.END)
        
        # Simple highlight effect
        for btn in self.choice_buttons.values():
            btn.itemconfig(1, outline=btn.bg)
        self.choice_buttons[choice].itemconfig(1, outline='#2d5a2d')
        
        # Auto-reset highlight after 2 seconds
        self.root.after(2000, lambda: self.choice_buttons[choice].itemconfig(1, outline=self.choice_buttons[choice].bg))
    
    def clear_history(self):
        self.choices.clear()
        self.choice_listbox.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = ChoiceTimerApp(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
