import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog
from pynput.keyboard import Listener as KeyboardListener, Key
import pyautogui
import threading
from datetime import datetime

class ColorPicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Picker")
        self.root.geometry("600x350")  # Adjusted window size
        self.root.configure(bg="#333333")

        # Add Logo and Author Labels
        self.set_favicon("fav.ico")  # Specify the path to your .ico file
        self.logo_label = tk.Label(root, text="Color Picker", fg="#FFFFFF", bg="#333333", font=("Arial", 24, "bold"))
        self.logo_label.pack()

        self.author_label = tk.Label(root, text="by Nokami", fg="#FFFFFF", bg="#333333", font=("Arial", 12))
        self.author_label.pack()

        self.info_label_frame = tk.Frame(root, bg="#333333")
        self.info_label_frame.pack(side=tk.TOP, pady=10)

        self.info_label = tk.Label(self.info_label_frame, text="Hint: Press F1 to save the color where the pointer is.", fg="#FFFFFF", bg="#333333", font=("Arial", 10))
        self.info_label.pack()

        self.button_frame = tk.Frame(root, bg="#333333")
        self.button_frame.pack(side=tk.TOP, pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start", command=self.start_bot, bg="#4CAF50", fg="white", font=("Arial", 14))
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_bot, state=tk.DISABLED, bg='#DC143C', font=("Arial", 14))
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.history_button = tk.Button(self.button_frame, text="Show History", command=self.show_history, bg="#3498db", fg="white", font=("Arial", 14))
        self.history_button.pack(side=tk.LEFT, padx=10)

        self.export_button = tk.Button(self.button_frame, text="Export", command=self.export_full_history, bg="#3498db", fg="white", font=("Arial", 14))
        self.export_button.pack(side=tk.LEFT, padx=10)

        self.status_label_frame = tk.Frame(root, bg="#333333")
        self.status_label_frame.pack(pady=10)

        self.status_label = tk.Label(self.status_label_frame, text="", fg="#008000", bg="#333333", font=("Arial", 16, "bold"))
        self.status_label.pack()

        self.pixel_color_label_frame = tk.Frame(root, bg="#333333")
        self.pixel_color_label_frame.pack(pady=10)

        self.pixel_color_label = tk.Label(self.pixel_color_label_frame, text="", fg="#008000", bg="#333333", font=("Arial", 16))
        self.pixel_color_label.pack()

        self.last_f1_color_label_frame = tk.Frame(root, bg="#333333")
        self.last_f1_color_label_frame.pack(pady=10)

        self.last_f1_color_label = tk.Label(self.last_f1_color_label_frame, text="", fg="#FFFFFF", bg="#333333", font=("Arial", 14))
        self.last_f1_color_label.pack()

        self.is_running = False
        self.interval = 1000
        self.active_history = []  # History including only the colors captured when the script is active
        self.f1_history = []  # History for F1 button pressed colors
        self.last_f1_color = None

        # Set up threading for keyboard listener
        self.keyboard_thread = threading.Thread(target=self.start_keyboard_listener)
        self.keyboard_thread.daemon = True  # Daemonize thread to allow program exit

        # Start the main loop
        self.root.after(0, self.check_keyboard)
        self.root.mainloop()

    def set_favicon(self, path):
        try:
            self.root.iconbitmap(path)
        except tk.TclError as e:
            print(f"Error setting favicon: {e}")

    def start_keyboard_listener(self):
        with KeyboardListener(on_press=self.on_key_press) as listener:
            listener.join()

    def check_keyboard(self):
        if self.is_running:
            x, y = pyautogui.position()
            pixel_color = pyautogui.pixel(x, y)
            print(f"Pixel color at ({x}, {y}): {pixel_color}")

            self.pixel_color_label.config(text=f"Pixel Color: {pixel_color}")

            timestamp = datetime.now().strftime("%H:%M:%S")
            self.active_history.append((timestamp, pixel_color, "Active"))
            if self.last_f1_color is not None:
                self.last_f1_color_label.config(text=f"Last F1 Color: {self.last_f1_color}")

        # Call the check_keyboard function after a delay
        self.root.after(self.interval, self.check_keyboard)

    def on_key_press(self, key):
        if key == Key.f1:
            x, y = pyautogui.position()
            f1_color = pyautogui.pixel(x, y)
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Add F1 color to both F1 history and active history
            self.f1_history.append((timestamp, f1_color, "F1 Key"))
            self.active_history.append((timestamp, f1_color, "F1 Key"))

            self.last_f1_color = f1_color
            self.show_color_info(f1_color)

    def show_color_info(self, pixel_color):
        color_str = f"RGB: {pixel_color[0]}, {pixel_color[1]}, {pixel_color[2]}"

        color_window = tk.Toplevel(self.root)
        color_window.title("Color Information")
        color_window.geometry("200x100")
        color_window.configure(bg="#333333")

        color_label = tk.Label(color_window, text=color_str, fg="#FFFFFF", bg="#333333", font=("Arial", 12))
        color_label.pack(pady=20)

    def start_bot(self):
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start the keyboard listener thread
        self.keyboard_thread.start()

    def stop_bot(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED, fg="black")
        self.status_label.config(text="Inactive")
        self.pixel_color_label.config(text="")
        self.last_f1_color_label.config(text="")

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("History")

        tree = ttk.Treeview(
            history_window,
            columns=("RGB", "Source", "Time"),
            show="headings"
        )
        tree.heading("RGB", text="RGB")
        tree.heading("Source", text="Source")
        tree.heading("Time", text="Time")

        tree.pack(expand=True, fill=tk.BOTH)

        for timestamp, color, source in self.active_history:
            rgb_str = f"{color[0]}, {color[1]}, {color[2]}"
            tree.insert("", "end", values=(rgb_str, "Default", timestamp))

        for timestamp, color, source in self.f1_history:
            rgb_str = f"{color[0]}, {color[1]}, {color[2]}"
            tree.insert("", "end", values=(rgb_str, "F1 Key", timestamp))

    def export_full_history(self):
        if self.active_history or self.f1_history:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

            if file_path:
                with open(file_path, "w") as file:
                    for timestamp, color, source in self.active_history + self.f1_history:
                        color_str = f"Time: {timestamp}   RGB: {color[0]}, {color[1]}, {color[2]}   Source: {source}\n"
                        file.write(f"{color_str}")

                messagebox.showinfo("Export Successful", f"History exported to {file_path}")
        else:
            messagebox.showinfo("History", "No history available.")

if __name__ == "__main__":
    root = tk.Tk()
    color_picker = ColorPicker(root)
    root.mainloop()
