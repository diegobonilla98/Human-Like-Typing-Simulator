import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from utils import type_like_human
import os


def set_custom_theme():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 12, 'bold'), foreground='black')
    style.configure('TLabel', font=('Helvetica', 12), background='light gray', foreground='black')
    style.configure('TCheckbutton', font=('Helvetica', 12))
    style.configure('Vertical.TScale', background='light gray', foreground='black', troughcolor='gray')
    style.configure('TNotebook', tabposition='n')  # Position of the tab 'n' as in north
    style.map('TButton', background=[('active', 'gray'), ('!disabled', 'silver')])


class App:
    def __init__(self, root):
        self.root = root
        self.root.iconbitmap("icon.ico")
        self.root.title("Human Typing Simulator")
        self.root.geometry("800x500")
        set_custom_theme()

        # Tabs
        tab_control = ttk.Notebook(root)
        self.main_tab = ttk.Frame(tab_control)
        self.how_to_tab = ttk.Frame(tab_control)
        tab_control.add(self.main_tab, text="Main")
        tab_control.add(self.how_to_tab, text="How to Use")
        tab_control.pack(expand=1, fill="both")

        # How to Use tab content
        instructions = """Tools:
        - Type, paste or select the text file for the app to copy from.
        - Select the type speed, error rate parameters. By default, a mid-fast human writing is set.
        - The "Take Breaks" flag introduces rare stops of up to 5 minutes (simulating resting or research breaks).
        - Using the flag "Variable Speed" makes the speed less robotic and more human.
        - Add "**" or "*" at the beginning and end of words for italic or bold formatting like **this** or *that*.
        
        Instructions:
        1. Once the text is filled and the parameters set, click "START"
        2. A 5 second countdown starts and you have to click on the text editor for the simulator to start typing
        3. The "Terminate" button can stop the program anytime
        
        IF NOT TYPING HAPPENS, YOU MIGHT HAVE TO RUN THE PROGRAM WITH ADMIN PRIVILEGES.
        """
        how_to_label = tk.Label(self.how_to_tab, text=instructions, wraplength=750)
        how_to_label.pack(pady=20, padx=10)

        # Main tab layout with two columns
        self.column1 = tk.Frame(self.main_tab)
        self.column2 = tk.Frame(self.main_tab)
        self.column1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.column2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sliders and Checks in Column 1
        self.slider1 = tk.Scale(self.column1, from_=50, to=98, label="Type Speed", orient=tk.VERTICAL)
        self.slider1.set(80)
        self.slider1.pack(pady=10)
        self.slider2 = tk.Scale(self.column1, from_=0, to=10, label="Error Rate", orient=tk.VERTICAL)
        self.slider2.set(2)
        self.slider2.pack(pady=10)
        self.binary_var1 = tk.BooleanVar()
        self.binary_button1 = tk.Checkbutton(self.column1, text="Take Breaks", variable=self.binary_var1)
        self.binary_button1.pack(pady=10)
        self.binary_var2 = tk.BooleanVar()
        self.binary_button2 = tk.Checkbutton(self.column1, text="Variable Speed", variable=self.binary_var2)
        self.binary_button2.select()
        self.binary_button2.pack(pady=10)

        # Text field and buttons in Column 2
        self.text_field = tk.Text(self.column2, height=10, width=50)
        self.text_field.pack(pady=10)
        self.file_button = tk.Button(self.column2, text="Select Text File", command=self.load_text_file)
        self.file_button.pack(pady=5)
        self.start_button = tk.Button(self.column2, text="START!", command=self.initiate_start_process)
        self.start_button.pack(pady=10)
        self.terminate_button = tk.Button(self.column2, text="Terminate", command=self.terminate_process,
                                          state=tk.DISABLED)
        self.terminate_button.pack(pady=5)

        # Timer label
        self.timer_label = tk.Label(self.column2, text="00:00")
        self.timer_label.pack()

        # Internal state
        self.start_time = None
        self.process_thread = None
        self.stop_event = threading.Event()

    def load_text_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_field.delete(1.0, tk.END)
                self.text_field.insert(tk.END, file.read())

    def initiate_start_process(self):
        # Countdown from 5 before starting the process
        self.countdown(5)

    def countdown(self, count):
        if count > 0:
            self.start_button.config(state='disabled', text=f"Start ({count})")
            self.root.after(1000, self.countdown, count - 1)
        else:
            self.start_process()

    def start_process(self):
        self.start_button.config(text="START!")
        self.terminate_button.config(state='normal')
        self.start_time = time.time()
        self.stop_event.clear()

        # Start the timer and the process
        threading.Thread(target=self.run_timer).start()
        self.process_thread = threading.Thread(target=self.process_data)
        self.process_thread.start()

    def run_timer(self):
        start = time.time()
        while self.start_time:
            elapsed = time.time() - start
            minutes, seconds = divmod(int(elapsed), 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=time_str)
            time.sleep(1)

    def process_data(self):
        text = self.text_field.get("1.0", tk.END)
        slider1_val = float(self.slider1.get()) / 100.
        slider2_val = float(self.slider2.get()) / 100.
        option1_val = self.binary_var1.get()
        option2_val = self.binary_var2.get()

        print("Initializing typing:")
        print("\t- Text:", text[:20], "...")
        print("\t- Typing Speed:", slider1_val)
        print("\t- Error Rate:", slider2_val)
        print("\t- Make Speed Variable:", option2_val)
        print("\t- Simulate Breaks:", option1_val)

        type_like_human(text, speed=slider1_val, variable_speed=option2_val, error_rate=slider2_val, take_breaks=option1_val, stop_event=self.stop_event)

        if self.start_time:  # Check if the process has been terminated
            self.finish_process()

    def terminate_process(self):
        if self.process_thread.is_alive():
            self.stop_event.set()  # Signal the thread to stop
            self.timer_label.config(text="Terminated")
            self.start_button.config(state='normal')
            self.terminate_button.config(state='disabled')

    def finish_process(self):
        self.start_time = None
        elapsed_time = self.timer_label.cget("text")
        self.root.after(0, self.show_result, elapsed_time)

    def show_result(self, elapsed_time):
        response = messagebox.askyesno("Process Completed",
                                       f"Processing completed in {elapsed_time}.\nWould you like to run another process?")
        if response:
            self.reset_app()
        else:
            self.root.quit()

    def reset_app(self):
        self.timer_label.config(text="00:00")
        self.start_button.config(state='normal')
        self.terminate_button.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
