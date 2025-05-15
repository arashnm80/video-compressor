import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

FFMPEG_EXE_NAME = "ffmpeg.exe"

class VideoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("فشرده‌ساز ویدیو")
        self.root.geometry("400x250")  # افزایش سایز پنجره
        self.input_file = None

        # UI
        self.label = tk.Label(root, text="هیچ فایلی انتخاب نشده است.")
        self.label.pack(pady=10)

        self.select_button = tk.Button(root, text="انتخاب ویدیو", command=self.select_file)
        self.select_button.pack()

        # لیبل‌ها برای کیفیت
        crf_frame = tk.Frame(root)
        crf_frame.pack(pady=10)

        tk.Label(crf_frame, text="کیفیت بالا\nحجم بیشتر").pack(side=tk.LEFT, padx=5)

        self.crf_scale = tk.Scale(crf_frame, from_=20, to=30, orient=tk.HORIZONTAL, label="کیفیت (CRF)")
        self.crf_scale.set(25)
        self.crf_scale.pack(side=tk.LEFT)

        tk.Label(crf_frame, text="کیفیت پایین\nحجم کمتر").pack(side=tk.LEFT, padx=5)

        self.compress_button = tk.Button(root, text="فشرده‌سازی", command=self.compress_video)
        self.compress_button.pack(pady=5)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

    def select_file(self):
        filetypes = [("فایل‌های ویدیو", "*.mp4 *.mov *.mkv *.avi"), ("همه فایل‌ها", "*.*")]
        filepath = filedialog.askopenfilename(title="انتخاب ویدیو", filetypes=filetypes)
        if filepath:
            self.input_file = filepath
            self.label.config(text=f"فایل انتخاب‌شده: {os.path.basename(filepath)}")

    def get_ffmpeg_path(self):
        # ابتدا در مسیر برنامه بسته‌بندی شده بررسی کنید
        ffmpeg_path = resource_path(FFMPEG_EXE_NAME)
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path

        # اگر در مسیر پیش‌فرض نبود، در مسیر اجرای برنامه بررسی کنید
        if os.path.exists(FFMPEG_EXE_NAME):
            return FFMPEG_EXE_NAME

        # اگر همچنان پیدا نشد
        return None

    def compress_video(self):
        if not self.input_file:
            messagebox.showwarning("هشدار", "هیچ فایلی انتخاب نشده است.")
            return

        ffmpeg_path = self.get_ffmpeg_path()
        if not ffmpeg_path:
            messagebox.showerror("خطا", "فایل ffmpeg.exe پیدا نشد. لطفاً مطمئن شوید که در پوشه برنامه وجود دارد.")
            return

        output_file = os.path.splitext(self.input_file)[0] + "_compressed.mp4"
        crf_value = str(self.crf_scale.get())

        cmd = [
            ffmpeg_path,
            "-y",  # اضافه کردن پارامتر -y برای بازنویسی فایل در صورت وجود
            "-i", self.input_file,
            "-vcodec", "libx264",
            "-preset", "veryfast",
            "-crf", crf_value,
            output_file
        ]

        # بررسی وجود فایل قبلی
        if os.path.exists(output_file):
            self.status_label.config(text="فایل قبلی موجود است. در حال بازنویسی...")
        else:
            self.status_label.config(text="در حال فشرده‌سازی...")
        
        self.root.update()

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.status_label.config(text="فشرده‌سازی تمام شد!")
                messagebox.showinfo("موفقیت", f"ویدیو با موفقیت فشرده شد:\n{output_file}")
            else:
                self.status_label.config(text="خطا در فشرده‌سازی.")
                messagebox.showerror("خطا", result.stderr)
        except Exception as e:
            self.status_label.config(text="خطا")
            messagebox.showerror("خطا", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCompressorApp(root)
    root.mainloop()
