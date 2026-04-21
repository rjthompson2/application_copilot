from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from config import RESUME_FILE
from resume.resume import load_resume

# FILE PICKER
def pick_file():
    root = tk.Tk()
    root.withdraw()  # hide main window

    file_path = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=[
            ("All Supported", "*.pdf *.docx *.txt"),
            ("PDF files", "*.pdf"),
            ("Word files", "*.docx"),
            ("Text files", "*.txt"),
        ],
    )

    return file_path


# TEXT EXTRACTION
def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()

    if ext == ".txt":
        return Path(file_path).read_text(errors="ignore")

    if ext == ".pdf":
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if ext == ".docx":
        import docx

        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError(f"Unsupported file type: {ext}")


# MAIN LOGIC
def load_resume_interactive():
    choice = input("Do you want to upload a resume? (y/n): ").strip().lower()

    if choice != "y":
        print("Skipping resume upload.")
        return load_resume(RESUME_FILE)

    file_path = pick_file()

    if not file_path:
        print("No file selected.")
        return None

    print(f"Selected: {file_path}")

    text = extract_text(file_path)

    RESUME_FILE.write_text(text, encoding="utf-8")

    print(f"Resume saved to: {RESUME_FILE}")

    return text