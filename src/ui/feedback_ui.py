import tkinter as tk
from tkinter import messagebox
from src.logic.feedback import FeedbackManager

class FeedbackUI:
    def __init__(self, parent):
        self.parent = parent
        self.feedback_mgr = FeedbackManager()

        # Tiêu đề
        tk.Label(self.parent, text="PHẢN HỒI", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=3, pady=10)

        # Form nhập liệu
        tk.Label(self.parent, text="Mã NV:").grid(row=1, column=0, padx=5, pady=5)
        self.employee_id_entry = tk.Entry(self.parent)
        self.employee_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.parent, text="Phản hồi:").grid(row=2, column=0, padx=5, pady=5)
        self.feedback_entry = tk.Entry(self.parent)
        self.feedback_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.parent, text="Gửi phản hồi", command=self.add_feedback).grid(row=2, column=2, padx=5, pady=5)

        tk.Label(self.parent, text="Trả lời phản hồi:").grid(row=3, column=0, padx=5, pady=5)
        self.response_entry = tk.Entry(self.parent)
        self.response_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(self.parent, text="Gửi trả lời", command=self.add_response).grid(row=3, column=2, padx=5, pady=5)

        # Bảng hiển thị danh sách phản hồi
        self.feedback_listbox = tk.Listbox(self.parent, width=80, height=10)
        self.feedback_listbox.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

        # Hiển thị danh sách ban đầu
        self.load_feedbacks()

    def load_feedbacks(self):
        self.feedback_listbox.delete(0, tk.END)
        feedbacks = self.feedback_mgr.get_all_feedbacks_with_responses()
        for feedback in feedbacks:
            self.feedback_listbox.insert(tk.END, f"{feedback[0]} - {feedback[1]} - {feedback[2]} - Trả lời: {feedback[3]}")

    def add_feedback(self):
        employee_id = self.employee_id_entry.get()
        feedback = self.feedback_entry.get()
        if employee_id and feedback:
            self.feedback_mgr.add_feedback(employee_id, feedback)
            messagebox.showinfo("Thành công", "Gửi phản hồi thành công!")
            self.feedback_entry.delete(0, tk.END)
            self.load_feedbacks()
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã nhân viên và phản hồi!")

    def add_response(self):
        selected = self.feedback_listbox.get(tk.ACTIVE)
        if selected:
            feedback_id = selected.split(" - ")[0]
            response = self.response_entry.get()
            if response:
                self.feedback_mgr.add_response(feedback_id, response)
                messagebox.showinfo("Thành công", "Gửi trả lời thành công!")
                self.response_entry.delete(0, tk.END)
                self.load_feedbacks()
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập câu trả lời!")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phản hồi để trả lời!")