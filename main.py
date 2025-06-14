import sys
import os

# Thêm đường dẫn thư mục src vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from src.ui.main_window import HRApp

if __name__ == "__main__":
    import tkinter as tk
    root = tk.Tk()
    app = HRApp(root)
    root.mainloop()