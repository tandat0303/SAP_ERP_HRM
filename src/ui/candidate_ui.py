import tkinter as tk
from tkinter import messagebox
from src.logic.candidate import CandidateManager

class CandidateUI:
    def __init__(self, parent):
        self.parent = parent
        self.candidate_mgr = CandidateManager()

        # Tiêu đề
        tk.Label(self.parent, text="QUẢN LÝ ỨNG VIÊN", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Form nhập liệu
        tk.Label(self.parent, text="Tên:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(self.parent)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email_entry = tk.Entry(self.parent)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Vị trí ứng tuyển:").grid(row=3, column=0, padx=5, pady=5)
        self.position_entry = tk.Entry(self.parent)
        self.position_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Button(self.parent, text="Thêm ứng viên", command=self.add_candidate).grid(row=4, column=1, padx=5, pady=5)

        # Bảng hiển thị danh sách ứng viên
        self.candidate_listbox = tk.Listbox(self.parent, width=80, height=10)
        self.candidate_listbox.grid(row=5, column=0, columnspan=3, padx=5, pady=10)

        # Hiển thị danh sách ban đầu
        self.load_candidates()

    def load_candidates(self):
        self.candidate_listbox.delete(0, tk.END)
        self.candidate_mgr.db.execute("SELECT * FROM Candidates")
        for row in self.candidate_mgr.db.fetch_all():
            self.candidate_listbox.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - {row[4]}")

    def add_candidate(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        position = self.position_entry.get()
        if name and email and position:
            self.candidate_mgr.add_candidate(name, email, position)
            messagebox.showinfo("Thành công", "Thêm ứng viên thành công!")
            self.clear_entries()
            self.load_candidates()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin ứng viên!")

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)