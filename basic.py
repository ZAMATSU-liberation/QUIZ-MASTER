# =========================================================
#              QUIZMASTER PRO
#        AI + SQLITE + MODERN GUI + SCORES (ENHANCED)
# =========================================================

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont
import sqlite3
import random
import json
import os
import time
import threading
import urllib.request

# ========================================================
# DATABASE
# =========================================================

DB_NAME = "quizmasterpro.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    difficulty TEXT,
    score INTEGER,
    date TEXT
)
""")

conn.commit()

# =========================================================
# COLORS
# =========================================================

COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "accent": "#8b5cf6",
    "accent2": "#06b6d4",
    "text": "#f8fafc",
    "correct": "#22c55e",
    "wrong": "#ef4444",
    "gold": "#f59e0b",
    "easy": "#10b981",
    "medium": "#f59e0b",
    "hard": "#ef4444",
}

# =========================================================
# QUESTION BANK
# =========================================================

QUESTION_BANK = {
    "Easy": [
        {
            "q": "What is the capital of France?",
            "opts": ["Berlin", "Madrid", "Paris", "Rome"],
            "ans": "Paris"
        },
        {
            "q": "How many sides does a hexagon have?",
            "opts": ["5", "6", "7", "8"],
            "ans": "6"
        },
        {
            "q": "What is 10 + 5?",
            "opts": ["12", "13", "15", "20"],
            "ans": "15"
        },
        {
            "q": "What is the smallest prime number?",
            "opts": ["0", "1", "2", "3"],
            "ans": "2"
        },
        {
            "q": "Which planet is closest to the Sun?",
            "opts": ["Venus", "Mercury", "Earth", "Mars"],
            "ans": "Mercury"
        },
    ],

    "Medium": [
        {
            "q": "Who painted the Mona Lisa?",
            "opts": ["Van Gogh", "Da Vinci", "Picasso", "Raphael"],
            "ans": "Da Vinci"
        },
        {
            "q": "What is the square root of 144?",
            "opts": ["10", "11", "12", "13"],
            "ans": "12"
        },
        {
            "q": "Which country invented paper?",
            "opts": ["India", "China", "Egypt", "Japan"],
            "ans": "China"
        },
        {
            "q": "What is the largest ocean on Earth?",
            "opts": ["Atlantic", "Indian", "Arctic", "Pacific"],
            "ans": "Pacific"
        },
        {
            "q": "Who wrote Romeo and Juliet?",
            "opts": ["Marlowe", "Shakespeare", "Jonson", "Webster"],
            "ans": "Shakespeare"
        },
    ],

    "Hard": [
        {
            "q": "What does HTTP stand for?",
            "opts": [
                "HyperText Transfer Protocol",
                "High Text Transfer Package",
                "Hyper Tool Transfer Protocol",
                "Home Text Transmission Protocol"
            ],
            "ans": "HyperText Transfer Protocol"
        },
        {
            "q": "What year was Magna Carta signed?",
            "opts": ["1215", "1492", "1776", "1914"],
            "ans": "1215"
        },
        {
            "q": "Which philosopher wrote Critique of Pure Reason?",
            "opts": ["Kant", "Hegel", "Plato", "Aristotle"],
            "ans": "Kant"
        },
        {
            "q": "What is the chemical symbol for Gold?",
            "opts": ["Go", "Gd", "Au", "Ag"],
            "ans": "Au"
        },
        {
            "q": "Who discovered Penicillin?",
            "opts": ["Marie Curie", "Alexander Fleming", "Louis Pasteur", "Joseph Lister"],
            "ans": "Alexander Fleming"
        },
    ]
}

# =========================================================
# AI QUESTION FETCHER
# =========================================================

def fetch_ai_questions(difficulty, callback):

    def worker():

        try:

            prompt = (
                f"Generate 5 MCQ quiz questions for {difficulty} level. "
                f"Return ONLY valid JSON array with exactly these keys for each object: 'q', 'opts' (array of 4 strings), 'ans'. "
                f"No markdown, no code blocks, just pure JSON."
            )

            payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }).encode()

            request = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
            )

            response = urllib.request.urlopen(request)

            result = json.loads(response.read())

            text = ""

            for item in result["content"]:
                if item["type"] == "text":
                    text += item["text"]

            # Clean up markdown code blocks if present
            text = text.replace("```json", "").replace("```", "").strip()
            
            questions = json.loads(text)

            callback(questions)

        except Exception as e:
            print(f"Error fetching AI questions: {e}")
            callback(None)

    threading.Thread(target=worker, daemon=True).start()

# =========================================================
# MAIN APP
# =========================================================

class QuizMasterPro(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("⚡ QuizMaster Pro")
        self.geometry("1100x750")
        self.configure(bg=COLORS["bg"])

        self.score = 0
        self.question_index = 0
        self.questions = []
        self.difficulty = "Medium"
        self.selected_option = None
        self.option_buttons = []

        self.setup_fonts()

        self.show_home()

    # =====================================================
    # FONTS
    # =====================================================

    def setup_fonts(self):

        self.title_font = tkfont.Font(
            family="Arial",
            size=30,
            weight="bold"
        )

        self.question_font = tkfont.Font(
            family="Arial",
            size=16,
            weight="bold"
        )

        self.option_font = tkfont.Font(
            family="Arial",
            size=12
        )
        
        self.label_font = tkfont.Font(
            family="Arial",
            size=14,
            weight="bold"
        )

    # =====================================================
    # CLEAR SCREEN
    # =====================================================

    def clear_screen(self):

        for widget in self.winfo_children():
            widget.destroy()

    # =====================================================
    # HOME SCREEN
    # =====================================================

    def show_home(self):

        self.clear_screen()

        title = tk.Label(
            self,
            text="⚡ QuizMaster Pro",
            font=self.title_font,
            bg=COLORS["bg"],
            fg=COLORS["text"]
        )

        title.pack(pady=20)

        subtitle = tk.Label(
            self,
            text="AI + SQLite + Modern GUI Quiz System",
            font=("Arial", 14),
            bg=COLORS["bg"],
            fg=COLORS["accent2"]
        )

        subtitle.pack(pady=5)

        # Difficulty Buttons

        frame = tk.Frame(self, bg=COLORS["bg"])
        frame.pack(pady=30)

        easy_btn = tk.Button(
            frame,
            text="Easy",
            bg=COLORS["easy"],
            fg="white",
            width=15,
            font=("Arial", 13, "bold"),
            command=lambda: self.start_game("Easy")
        )

        easy_btn.grid(row=0, column=0, padx=10)

        medium_btn = tk.Button(
            frame,
            text="Medium",
            bg=COLORS["medium"],
            fg="white",
            width=15,
            font=("Arial", 13, "bold"),
            command=lambda: self.start_game("Medium")
        )

        medium_btn.grid(row=0, column=1, padx=10)

        hard_btn = tk.Button(
            frame,
            text="Hard",
            bg=COLORS["hard"],
            fg="white",
            width=15,
            font=("Arial", 13, "bold"),
            command=lambda: self.start_game("Hard")
        )

        hard_btn.grid(row=0, column=2, padx=10)

        # High Scores

        score_frame = tk.Frame(
            self,
            bg=COLORS["card"],
            padx=20,
            pady=20
        )

        score_frame.pack(pady=20)

        tk.Label(
            score_frame,
            text="🏆 High Scores",
            font=("Arial", 18, "bold"),
            bg=COLORS["card"],
            fg=COLORS["gold"]
        ).pack()

        easy_score = self.get_high_score("Easy")
        medium_score = self.get_high_score("Medium")
        hard_score = self.get_high_score("Hard")

        tk.Label(
            score_frame,
            text=f"Easy : {easy_score}",
            bg=COLORS["card"],
            fg="white",
            font=("Arial", 13)
        ).pack(pady=5)

        tk.Label(
            score_frame,
            text=f"Medium : {medium_score}",
            bg=COLORS["card"],
            fg="white",
            font=("Arial", 13)
        ).pack(pady=5)

        tk.Label(
            score_frame,
            text=f"Hard : {hard_score}",
            bg=COLORS["card"],
            fg="white",
            font=("Arial", 13)
        ).pack(pady=5)

    # =====================================================
    # START GAME
    # =====================================================

    def start_game(self, difficulty):

        self.difficulty = difficulty
        self.score = 0
        self.question_index = 0

        self.questions = QUESTION_BANK[difficulty].copy()

        random.shuffle(self.questions)

        self.show_question()

    # =====================================================
    # SHOW QUESTION
    # =====================================================

    def show_question(self):

        self.clear_screen()

        if self.question_index >= len(self.questions):
            self.show_result()
            return

        question_data = self.questions[self.question_index]

        # Top frame with score and difficulty
        top_frame = tk.Frame(self, bg=COLORS["card"], height=60)
        top_frame.pack(fill="x")

        tk.Label(
            top_frame,
            text=f"Question {self.question_index + 1}/{len(self.questions)}",
            bg=COLORS["card"],
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=20, pady=10)

        tk.Label(
            top_frame,
            text=f"Score: {self.score}",
            bg=COLORS["card"],
            fg="white",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=20)

        tk.Label(
            top_frame,
            text=f"Difficulty: {self.difficulty}",
            bg=COLORS["card"],
            fg=COLORS["gold"],
            font=("Arial", 12, "bold")
        ).pack(side="right", padx=20, pady=10)

        # Question frame
        question_frame = tk.Frame(
            self,
            bg=COLORS["card"],
            padx=30,
            pady=20
        )

        question_frame.pack(pady=20, padx=30, fill="x")

        tk.Label(
            question_frame,
            text=question_data["q"],
            font=self.question_font,
            bg=COLORS["card"],
            fg="white",
            wraplength=900,
            justify="left"
        ).pack(anchor="w")

        # Options frame
        option_frame = tk.Frame(self, bg=COLORS["bg"])
        option_frame.pack(pady=15, fill="both", expand=True, padx=50)

        self.option_buttons = []
        shuffled_options = question_data["opts"].copy()
        random.shuffle(shuffled_options)

        for option in shuffled_options:

            btn = tk.Button(
                option_frame,
                text=option,
                wraplength=700,
                justify="left",
                pady=15,
                padx=20,
                bg=COLORS["accent"],
                fg="white",
                font=self.option_font,
                relief="raised",
                bd=2,
                command=lambda opt=option: self.check_answer(opt, question_data["ans"])
            )

            btn.pack(pady=10, fill="x", padx=20)
            self.option_buttons.append(btn)

    # =====================================================
    # CHECK ANSWER
    # =====================================================

    def check_answer(self, chosen, correct):

        if chosen == correct:

            self.score += 10

            messagebox.showinfo(
                "Correct ✅",
                f"Great job! The correct answer is: {correct}"
            )

        else:

            messagebox.showerror(
                "Wrong ❌",
                f"Incorrect!\n\nYour answer: {chosen}\nCorrect answer: {correct}"
            )

        self.question_index += 1

        self.show_question()

    # =====================================================
    # SHOW RESULT
    # =====================================================

    def show_result(self):

        self.clear_screen()

        save_score(
            self.difficulty,
            self.score
        )

        result_frame = tk.Frame(
            self,
            bg=COLORS["card"],
            padx=40,
            pady=40
        )

        result_frame.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        tk.Label(
            result_frame,
            text="🏆 Quiz Finished!",
            font=self.title_font,
            bg=COLORS["card"],
            fg=COLORS["gold"]
        ).pack(pady=20)

        tk.Label(
            result_frame,
            text=f"Final Score: {self.score}",
            font=("Arial", 24, "bold"),
            bg=COLORS["card"],
            fg="white"
        ).pack(pady=10)

        percentage = int((self.score / (len(self.questions) * 10)) * 100)

        tk.Label(
            result_frame,
            text=f"Accuracy: {percentage}%",
            font=("Arial", 16),
            bg=COLORS["card"],
            fg=COLORS["correct"]
        ).pack(pady=10)

        play_again = tk.Button(
            result_frame,
            text="Play Again",
            bg=COLORS["accent"],
            fg="white",
            font=("Arial", 14, "bold"),
            width=20,
            pady=10,
            command=self.show_home
        )

        play_again.pack(pady=20)

        quit_btn = tk.Button(
            result_frame,
            text="Quit",
            bg=COLORS["wrong"],
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            pady=8,
            command=self.quit
        )

        quit_btn.pack(pady=10)

    # =====================================================
    # GET HIGH SCORE
    # =====================================================

    def get_high_score(self, difficulty):

        cursor.execute("""
        SELECT MAX(score)
        FROM scores
        WHERE difficulty=?
        """, (difficulty,))

        result = cursor.fetchone()[0]

        if result is None:
            return 0

        return result

# =========================================================
# SAVE SCORE
# =========================================================

def save_score(difficulty, score):

    date = time.strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
    INSERT INTO scores(difficulty, score, date)
    VALUES(?, ?, ?)
    """, (difficulty, score, date))

    conn.commit()

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":

    app = QuizMasterPro()

    app.mainloop()
 
