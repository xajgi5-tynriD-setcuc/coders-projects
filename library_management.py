import os
import sys 
from colorama import init, Fore, Style
init(autoreset=True)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QListWidget, QTextEdit, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
 

 
books = [
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "issued": False},
    {"title": "1984", "author": "George Orwell", "issued": False},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "issued": False},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "issued": False},
    {"title": "Moby-Dick", "author": "Herman Melville", "issued": False}
]
members = [
    {"id": "M001", "name": "koba christian", "borrowed_books": []},
    {"id": "M002", "name": "roni aidoo", "borrowed_books": []},
    {"id": "M003", "name": "nathenial mensah", "borrowed_books": []},
    {"id": "M004", "name": "eleazer", "borrowed_books": []},
    {"id": "M005", "name": "snr calib", "borrowed_books": []}
]

LIBRARIAN_PASSWORD = "admin123"  # Change this password as needed

# New GUI components
class LoginWidget(QWidget):
    def __init__(self, success_callback):
        super().__init__()
        self.success_callback = success_callback
        layout = QVBoxLayout()
        self.lbl = QLabel("Enter Librarian Password:")
        layout.addWidget(self.lbl)
        self.pwd_edit = QLineEdit()
        self.pwd_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pwd_edit)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.check_password)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)
    
    def check_password(self):
        if self.pwd_edit.text() == LIBRARIAN_PASSWORD:
            QMessageBox.information(self, "Success", "Access granted.")
            self.success_callback()
        else:
            QMessageBox.warning(self, "Error", "Incorrect password.")

class MainMenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        # Create buttons for each action
        btn_layout = QVBoxLayout()
        actions = [
            ("Add Book", self.add_book),
            ("List Books", self.list_books),
            ("Add Member", self.add_member),
            ("List Members", self.list_members),
            ("Issue Book", self.issue_book),
            ("Return Book", self.return_book),
            ("Search Books", self.search_books),
            ("Exit", self.exit_app)
        ]
        for text, func in actions:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def add_book(self):
        title, ok1 = QInputDialog.getText(self, "Add Book", "Enter Book Title:")
        if not ok1 or not title:
            return
        author, ok2 = QInputDialog.getText(self, "Add Book", "Enter Author:")
        if not ok2 or not author:
            return
        books.append({"title": title, "author": author, "issued": False})
        self.log.append(f"Book '{title}' added.")
    
    def list_books(self):
        self.log.append("Listing Books:")
        for idx, book in enumerate(books):
            status = "Issued" if book["issued"] else "Available"
            self.log.append(f"{idx+1}. {book['title']} by {book['author']} - {status}")
    
    def add_member(self):
        name, ok = QInputDialog.getText(self, "Add Member", "Enter Member Name:")
        if not ok or not name:
            return
        member_id = f"M{len(members)+1:03d}"
        members.append({"id": member_id, "name": name, "borrowed_books": []})
        self.log.append(f"Member '{name}' added with ID {member_id}.")
    
    def list_members(self):
        self.log.append("Listing Members:")
        for member in members:
            self.log.append(f"ID: {member['id']} | Name: {member['name']} | Borrowed: {len(member['borrowed_books'])}")
    
    def issue_book(self):
        # Select book via input dialog (display existing books)
        book_idx, ok = QInputDialog.getInt(self, "Issue Book", "Enter book number to issue:", 1, 1, len(books))
        if not ok:
            return
        book = books[book_idx-1]
        if book["issued"]:
            QMessageBox.warning(self, "Error", "Book already issued.")
            return
        member_id, ok = QInputDialog.getText(self, "Issue Book", "Enter member ID:")
        if not ok or not member_id:
            return
        member = next((m for m in members if m["id"] == member_id), None)
        if not member:
            QMessageBox.warning(self, "Error", "Member not found.")
            return
        book["issued"] = True
        member["borrowed_books"].append(book["title"])
        self.log.append(f"Book '{book['title']}' issued to {member['name']}.")
    
    def return_book(self):
        member_id, ok = QInputDialog.getText(self, "Return Book", "Enter member ID:")
        if not ok or not member_id:
            return
        member = next((m for m in members if m["id"] == member_id), None)
        if not member:
            QMessageBox.warning(self, "Error", "Member not found.")
            return
        if not member["borrowed_books"]:
            QMessageBox.information(self, "Info", "This member has no borrowed books.")
            return
        # Show list of borrowed books and choose one
        book_titles = "\n".join(f"{i+1}. {title}" for i, title in enumerate(member["borrowed_books"]))
        choice, ok = QInputDialog.getInt(self, "Return Book", f"Borrowed books:\n{book_titles}\nEnter number of book to return:", 1, 1, len(member["borrowed_books"]))
        if not ok:
            return
        title = member["borrowed_books"].pop(choice-1)
        for book in books:
            if book["title"] == title and book["issued"]:
                book["issued"] = False
                self.log.append(f"Book '{title}' returned.")
                return
        self.log.append("Book not found in library records.")
    
    def search_books(self):
        query, ok = QInputDialog.getText(self, "Search Books", "Enter title or author to search:")
        if not ok or not query:
            return
        query = query.lower()
        found = False
        self.log.append("Search Results:")
        for idx, book in enumerate(books):
            if query in book["title"].lower() or query in book["author"].lower():
                status = "Issued" if book["issued"] else "Available"
                self.log.append(f"{idx+1}. {book['title']} by {book['author']} - {status}")
                found = True
        if not found:
            self.log.append("No books found matching your query.")
    
    def exit_app(self):
        QApplication.quit()

class LibraryManagementGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setGeometry(100, 100, 600, 500)
        self.login_widget = LoginWidget(self.show_main_menu)
        self.setCentralWidget(self.login_widget)
    
    def show_main_menu(self):
        self.main_menu = MainMenuWidget()
        self.setCentralWidget(self.main_menu)


        self.setWindowIcon(QIcon('images/library.jpg'))

# The main() function is replaced for GUI.
if __name__ == "__main__":
    app = QApplication([])
    window = LibraryManagementGUI()
    window.show()
    app.exec_()