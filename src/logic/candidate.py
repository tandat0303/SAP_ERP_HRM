from src.db.database import Database
import datetime

class CandidateManager:
    def __init__(self):
        self.db = Database()

    def add_candidate(self, name, email, position):
        candidate_id = f"CAN{len(self.db.fetch_all('SELECT * FROM Candidates')) + 1}"
        application_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.db.execute("INSERT INTO Candidates (candidate_id, name, email, position, application_date) VALUES (?, ?, ?, ?, ?)",
                        (candidate_id, name, email, position, application_date))