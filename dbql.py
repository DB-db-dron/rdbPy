from functools import cache
import sqlite3, uuid


class QuestionAnswerDatabase:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS questions (
                                id TEXT PRIMARY KEY,
                                question TEXT
                            )"""
        )
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS answers (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                question_id INTEGER,
                                answer TEXT,
                                FOREIGN KEY (question_id) REFERENCES questions(id)
                            )"""
        )
        self.conn.commit()

    def create_question(self, question):
        insert_sql = "INSERT INTO questions (id, question) VALUES (?, ?)"
        self.cursor.execute(
            insert_sql,
            (
                str(uuid.uuid4()),
                question,
            ),
        )
        self.conn.commit()
        print("Question inserted successfully.")

    def create_answer(self, question_id, answer):
        insert_sql = "INSERT INTO answers (question_id, answer) VALUES (?, ?)"
        self.cursor.execute(insert_sql, (question_id, answer))
        self.conn.commit()
        print("Answer inserted successfully.")

    def read_questions(self):
        select_sql = "SELECT id, question FROM questions"
        self.cursor.execute(select_sql)
        rows = self.cursor.fetchall()
        questions = [{"id": row[0], "question": row[1]} for row in rows]
        return questions

    def update_answer(self, answer_id, new_answer):
        update_sql = "UPDATE answers SET answer = ? WHERE id = ?"
        self.cursor.execute(update_sql, (new_answer, answer_id))
        self.conn.commit()
        print("Answer updated successfully.")

    def delete_answer(self, answer_id):
        delete_sql = "DELETE FROM answers WHERE id = ?"
        self.cursor.execute(delete_sql, (answer_id,))
        self.conn.commit()
        print("Answer deleted successfully.")

    def delete_question_and_answers(self, question_id):
        try:
            self.conn.execute("BEGIN")
            delete_question_sql = "DELETE FROM questions WHERE id = ?"
            self.conn.execute(delete_question_sql, (question_id,))
            delete_answers_sql = "DELETE FROM answers WHERE question_id = ?"
            self.conn.execute(delete_answers_sql, (question_id,))
            self.conn.commit()
            print("Question and its answers deleted successfully.")
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error occurred while deleting the question and its answers:", e)

    def get_answers_for_question(self, question_id):
        select_sql = """SELECT q.question, a.id, a.answer
                        FROM questions q LEFT JOIN answers a ON q.id = a.question_id
                        WHERE q.id = ?"""
        self.cursor.execute(select_sql, (question_id,))
        rows = self.cursor.fetchall()

        question = None
        answers = []
        for row in rows:
            if not question:
                question = row[0]
            if row[1] and row[2]:
                answer = {"id": row[1], "answer": row[2]}
                answers.append(answer)

        return {"question": question, "answers": answers}

    def close(self):
        self.conn.close()
