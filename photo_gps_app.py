# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import logging
from datetime import datetime, timezone
from tkinterdnd2 import DND_FILES, TkinterDnD
from gps_parser import GPSParser, GPSPoint
from exif_handler import ExifHandler
from gps_matcher import GPSMatcher

class PhotoGPSApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Photo GPS Writer")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        self.gps_file_path = None
        self.photo_files = []
        self.gps_points = []
        self.log_messages = []
        
        self.setup_logging()
        self.setup_ui()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        bg_color = "#f0f2f5"
        card_bg = "#ffffff"
        accent_color = "#0078d4"
        text_color = "#323130"
        light_text = "#605e5c"
        border_color = "#e1dfdd"
        
        self.root.configure(bg=bg_color)
        
        style.configure("Card.TFrame", background=card_bg)
        style.configure("Title.TLabel", background=bg_color, foreground=text_color, font=('Segoe UI', 16, 'bold'))
        style.configure("Section.TLabel", background=card_bg, foreground=text_color, font=('Segoe UI', 12, 'bold'))
        style.configure("Normal.TLabel", background=card_bg, foreground=text_color, font=('Segoe UI', 9))
        style.configure("Light.TLabel", background=card_bg, foreground=light_text, font=('Segoe UI', 9))
        style.configure("BG.TLabel", background=bg_color, foreground=text_color, font=('Segoe UI', 9))
        
        style.configure("Accent.TButton", foreground="#ffffff", background=accent_color, font=('Segoe UI', 9))
        style.map("Accent.TButton", background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
        style.configure("Normal.TButton", foreground=text_color, background="#ffffff", font=('Segoe UI', 9), borderwidth=1)
        style.map("Normal.TButton", background=[('active', '#f3f2f1'), ('pressed', '#e1dfdd')])
        
        style.configure("Card.TSeparator", background=border_color)
        style.configure("Custom.Horizontal.TProgressbar", troughcolor="#e1dfdd", background=accent_color, thickness=8)
        
        main_container = ttk.Frame(self.root, padding=20)
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(4, weight=1)

        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(header_frame, text="Photo GPS Writer", style="Title.TLabel").pack(side=tk.LEFT)

        gps_card = ttk.Frame(main_container, style="Card.TFrame", padding=20)
        gps_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        gps_card.columnconfigure(0, weight=1)
        
        ttk.Label(gps_card, text="1. GPS Track File", style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        self.gps_file_label = ttk.Label(gps_card, text="No GPS file selected", style="Light.TLabel")
        self.gps_file_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 15))
        
        gps_btn_frame = ttk.Frame(gps_card, style="Card.TFrame")
        gps_btn_frame.grid(row=1, column=1)
        
        ttk.Button(gps_btn_frame, text="Select File", style="Normal.TButton", command=self.select_gps_file, width=12).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(gps_btn_frame, text="Rename GPX", style="Normal.TButton", command=self.rename_gpx, width=12).grid(row=0, column=1)
        
        self.gps_time_range_label = ttk.Label(gps_card, text="", style="Light.TLabel")
        self.gps_time_range_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))

        photo_card = ttk.Frame(main_container, style="Card.TFrame", padding=20)
        photo_card.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        photo_card.columnconfigure(0, weight=1)
        
        ttk.Label(photo_card, text="2. Photo Files", style="Section.TLabel").grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))
        
        self.photo_count_label = ttk.Label(photo_card, text="No photo files selected", style="Light.TLabel")
        self.photo_count_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 15))
        
        photo_btn_frame = ttk.Frame(photo_card, style="Card.TFrame")
        photo_btn_frame.grid(row=1, column=1)
        
        ttk.Button(photo_btn_frame, text="Select Files", style="Normal.TButton", command=self.select_photos, width=12).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(photo_btn_frame, text="Select Folder", style="Normal.TButton", command=self.select_photo_folder, width=12).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(photo_btn_frame, text="Clear", style="Normal.TButton", command=self.clear_photos, width=8).grid(row=0, column=2)
        
        self.photo_time_range_label = ttk.Label(photo_card, text="", style="Light.TLabel")
        self.photo_time_range_label.grid(row=2, column=0, sticky=tk.W, padx=(0, 15), pady=(5, 0))

        settings_card = ttk.Frame(main_container, style="Card.TFrame", padding=20)
        settings_card.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_card.columnconfigure(1, weight=1)
        settings_card.columnconfigure(3, weight=1)
        
        ttk.Label(settings_card, text="Settings", style="Section.TLabel").grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 15))
        
        ttk.Label(settings_card, text="Time Offset (hours):", style="Normal.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.time_offset_var = tk.DoubleVar(value=0)
        ttk.Spinbox(settings_card, from_=-24, to=24, increment=0.5, textvariable=self.time_offset_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(0, 30))
        ttk.Label(settings_card, text="(Adjust photo time to match GPS time zone)", style="Light.TLabel").grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(2, 0))
        
        ttk.Label(settings_card, text="Max Time Diff (seconds):", style="Normal.TLabel").grid(row=1, column=2, sticky=tk.W, padx=(0, 10))
        self.max_time_diff_var = tk.IntVar(value=10)
        ttk.Spinbox(settings_card, from_=1, to=86400, increment=1, textvariable=self.max_time_diff_var, width=10).grid(row=1, column=3, sticky=tk.W)
        ttk.Label(settings_card, text="(Maximum time difference between photo and GPS point)", style="Light.TLabel").grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(2, 0))

        log_card = ttk.Frame(main_container, style="Card.TFrame", padding=20)
        log_card.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        log_card.columnconfigure(0, weight=1)
        log_card.rowconfigure(1, weight=1)
        
        ttk.Label(log_card, text="3. Processing Log", style="Section.TLabel").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_card, 
            wrap=tk.WORD, 
            font=('Consolas', 9),
            bg="#f8f9fa",
            fg="#323130",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.log_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        progress_frame = ttk.Frame(log_card, style="Card.TFrame")
        progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 15))
        
        self.status_label = ttk.Label(progress_frame, text="Ready", style="Light.TLabel")
        self.status_label.grid(row=0, column=1)

        bottom_frame = ttk.Frame(main_container)
        bottom_frame.grid(row=5, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(bottom_frame, text="Start Processing", style="Accent.TButton", command=self.start_processing, width=18).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(bottom_frame, text="Save Log", style="Normal.TButton", command=self.save_log, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(bottom_frame, text="Clear Log", style="Normal.TButton", command=self.clear_log, width=12).pack(side=tk.LEFT)

        self.setup_drag_drop()
        self.log("Program started, waiting for operation...")

    def setup_drag_drop(self):
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            file_path = file_path.strip('{}')
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ('.gpx', '.fit'):
                self.add_gps_file(file_path)
            elif ExifHandler.is_photo_file(file_path):
                self.add_photo_file(file_path)
            elif os.path.isdir(file_path):
                self.scan_photo_folder(file_path)

    def log(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        self.log_messages.append(log_line)
        self.log_text.insert(tk.END, log_line + "\n")
        self.log_text.see(tk.END)
        
        if level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)

    def select_gps_file(self):
        file_path = filedialog.askopenfilename(
            title="Select GPS Track File",
            filetypes=[("GPS Files", "*.gpx *.fit"), ("GPX Files", "*.gpx"), ("FIT Files", "*.fit"), ("All Files", "*.*")]
        )
        if file_path:
            self.add_gps_file(file_path)

    def add_gps_file(self, file_path: str):
        try:
            self.gps_file_path = file_path
            self.gps_file_label.config(text=os.path.basename(file_path), style="Normal.TLabel")
            self.log(f"Loading GPS file: {file_path}")
            
            self.gps_points = GPSParser.parse(file_path)
            self.log(f"Successfully parsed {len(self.gps_points)} GPS points")
            
            if self.gps_points:
                times = [p.time for p in self.gps_points]
                start_time = min(times).strftime("%Y-%m-%d %H:%M:%S")
                end_time = max(times).strftime("%Y-%m-%d %H:%M:%S")
                self.log(f"Track time range: {start_time} to {end_time}")
                self.gps_time_range_label.config(text=f"Time range: {start_time} to {end_time}", style="Normal.TLabel")
            else:
                self.gps_time_range_label.config(text="", style="Light.TLabel")
        except Exception as e:
            self.log(f"Failed to load GPS file: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to load GPS file: {str(e)}")
            self.gps_time_range_label.config(text="", style="Light.TLabel")

    def rename_gpx(self):
        if not self.gps_file_path or not self.gps_file_path.lower().endswith('.gpx'):
            messagebox.showwarning("Warning", "Please select a GPX file first")
            return
        
        try:
            new_path = GPSParser.rename_gpx_by_time(self.gps_file_path)
            if new_path != self.gps_file_path:
                self.gps_file_path = new_path
                self.gps_file_label.config(text=os.path.basename(new_path), style="Normal.TLabel")
                self.log(f"GPX file renamed to: {os.path.basename(new_path)}")
                messagebox.showinfo("Success", f"GPX file renamed to: {os.path.basename(new_path)}")
            else:
                self.log("GPX file does not need renaming", "WARNING")
                messagebox.showinfo("Info", "GPX file does not need renaming")
        except Exception as e:
            self.log(f"Failed to rename GPX file: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to rename GPX file: {str(e)}")

    def select_photos(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Photo Files",
            filetypes=[
                ("Photo Files", "*.jpg *.jpeg *.png *.tif *.tiff *.cr2 *.nef *.arw *.dng"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("PNG Files", "*.png"),
                ("TIFF Files", "*.tif *.tiff"),
                ("RAW Files", "*.cr2 *.nef *.arw *.dng"),
                ("All Files", "*.*")
            ]
        )
        for file_path in file_paths:
            self.add_photo_file(file_path)

    def select_photo_folder(self):
        folder_path = filedialog.askdirectory(title="Select Photo Folder")
        if folder_path:
            self.scan_photo_folder(folder_path)

    def scan_photo_folder(self, folder_path: str):
        count = 0
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if ExifHandler.is_photo_file(file_path):
                    self.add_photo_file(file_path)
                    count += 1
        self.log(f"Scanned {count} photos from folder")

    def add_photo_file(self, file_path: str):
        if file_path not in self.photo_files:
            self.photo_files.append(file_path)
            self.update_photo_count()

    def clear_photos(self):
        self.photo_files = []
        self.update_photo_count()
        self.log("Photo list cleared")

    def get_photo_time_range(self):
        if not self.photo_files:
            return None, None
        
        photo_times = []
        for photo_path in self.photo_files:
            photo_time = ExifHandler.get_photo_time(photo_path)
            if photo_time:
                photo_times.append(photo_time)
        
        if photo_times:
            return min(photo_times), max(photo_times)
        else:
            return None, None

    def update_photo_time_range(self):
        start_time, end_time = self.get_photo_time_range()
        if start_time and end_time:
            start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            self.photo_time_range_label.config(text=f"Time range: {start_str} to {end_str}", style="Normal.TLabel")
        else:
            self.photo_time_range_label.config(text="Cannot determine time range", style="Light.TLabel")

    def update_photo_count(self):
        if self.photo_files:
            self.photo_count_label.config(text=f"Selected {len(self.photo_files)} photos", style="Normal.TLabel")
            self.update_photo_time_range()
        else:
            self.photo_count_label.config(text="No photo files selected", style="Light.TLabel")
            self.photo_time_range_label.config(text="", style="Light.TLabel")

    def start_processing(self):
        if not self.gps_file_path:
            messagebox.showwarning("Warning", "Please select a GPS track file first")
            return
        if not self.photo_files:
            messagebox.showwarning("Warning", "Please select photo files first")
            return
        
        thread = threading.Thread(target=self.process_photos)
        thread.daemon = True
        thread.start()

    def process_photos(self):
        try:
            self.root.after(0, lambda: self.status_label.config(text="Processing..."))
            self.log("=" * 50)
            self.log("Starting photo processing...")
            
            matcher = GPSMatcher(self.gps_points)
            time_offset = self.time_offset_var.get()
            max_time_diff = self.max_time_diff_var.get()
            
            success_count = 0
            fail_count = 0
            skip_count = 0
            total = len(self.photo_files)
            
            for i, photo_path in enumerate(self.photo_files):
                progress = (i + 1) / total * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda s=f"Processing: {i+1}/{total}": self.status_label.config(text=s))
                
                try:
                    photo_time = ExifHandler.get_photo_time(photo_path)
                    if not photo_time:
                        self.log(f"Cannot get photo time: {os.path.basename(photo_path)}", "WARNING")
                        skip_count += 1
                        continue
                    
                    if time_offset != 0:
                        from datetime import timedelta
                        photo_time = photo_time + timedelta(hours=time_offset)
                    
                    point = matcher.find_closest_point(photo_time, max_time_diff)
                    if not point:
                        self.log(f"No matching GPS point found: {os.path.basename(photo_path)}", "WARNING")
                        skip_count += 1
                        continue
                    
                    if ExifHandler.write_gps_to_exif(photo_path, point):
                        time_diff = abs((point.time - photo_time).total_seconds())
                        self.log(f"Success: {os.path.basename(photo_path)} (time diff: {time_diff:.1f}s, location: {point.lat:.6f}, {point.lon:.6f})")
                        success_count += 1
                    else:
                        self.log(f"Failed to write EXIF: {os.path.basename(photo_path)}", "ERROR")
                        fail_count += 1
                        
                except Exception as e:
                    self.log(f"Processing failed: {os.path.basename(photo_path)} - {str(e)}", "ERROR")
                    fail_count += 1
            
            self.log("=" * 50)
            self.log(f"Processing complete: success {success_count}, failed {fail_count}, skipped {skip_count}")
            self.root.after(0, lambda: self.status_label.config(text="Complete"))
            
            messagebox.showinfo("Complete", f"Processing complete!\nSuccess: {success_count}\nFailed: {fail_count}\nSkipped: {skip_count}")
            
        except Exception as e:
            self.log(f"Error during processing: {str(e)}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error during processing: {str(e)}"))
        finally:
            self.root.after(0, lambda: self.progress_var.set(0))

    def save_log(self):
        if not self.log_messages:
            messagebox.showinfo("Info", "No log to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.log_messages))
                self.log(f"Log saved to: {file_path}")
                messagebox.showinfo("Success", "Log saved")
            except Exception as e:
                self.log(f"Failed to save log: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Failed to save log: {str(e)}")

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log_messages = []

    def run(self):
        self.root.mainloop()
