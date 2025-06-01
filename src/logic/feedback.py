from src.db.database import Database

class FeedbackManager:
    def __init__(self):
        self.db = Database()

    def add_feedback(self, employee_id, feedback):
        feedback_id = f"FB{len(self.db.fetch_all('SELECT * FROM Feedback')) + 1}"
        self.db.execute("INSERT INTO Feedback (feedback_id, employee_id, feedback) VALUES (?, ?, ?)",
                        (feedback_id, employee_id, feedback))

    def add_response(self, feedback_id, response):
        response_id = f"RES{len(self.db.fetch_all('SELECT * FROM AdminResponses')) + 1}"
        self.db.execute("INSERT INTO AdminResponses (response_id, feedback_id, response) VALUES (?, ?, ?)",
                        (response_id, feedback_id, response))

    def get_all_feedbacks_with_responses(self):
        self.db.execute("""
            SELECT f.feedback_id, f.employee_id, f.feedback, COALESCE(r.response, 'Chưa có trả lời')
            FROM Feedback f LEFT JOIN AdminResponses r ON f.feedback_id = r.feedback_id
        """)
        return self.db.fetch_all()