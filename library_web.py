from flask import Flask, render_template_string, request, redirect, url_for, session, send_file, flash
import os
import time
from werkzeug.utils import secure_filename
import datetime
import csv
from io import StringIO

app = Flask(__name__, static_folder='static')
app.secret_key = "your_secret_key_here"  # Change this to a random secret string

LIBRARIAN_USERNAME = "mama doris"
LIBRARIAN_PASSWORD = "doris@2024"

books = [
    {"title": "To Kill a Mockingbird", "author": "Harper Lee", "issued": False},
    {"title": "1984", "author": "George Orwell", "issued": False},
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "issued": False},
    {"title": "Pride and Prejudice", "author": "Jane Austen", "issued": False},
    {"title": "Moby-Dick", "author": "Herman Melville", "issued": False},
    {"title": "War and Peace", "author": "Leo Tolstoy", "issued": False},
    {"title": "The Catcher in the Rye", "author": "J.D. Salinger", "issued": False},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "issued": False},
    {"title": "Brave New World", "author": "Aldous Huxley", "issued": False},
    {"title": "Jane Eyre", "author": "Charlotte Brontë", "issued": False},
    {"title": "Wuthering Heights", "author": "Emily Brontë", "issued": False},
    {"title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "issued": False},
    {"title": "The Odyssey", "author": "Homer", "issued": False},
    {"title": "Great Expectations", "author": "Charles Dickens", "issued": False},
    {"title": "Little Women", "author": "Louisa May Alcott", "issued": False},
    {"title": "Animal Farm", "author": "George Orwell", "issued": False},
    {"title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "issued": False},
    {"title": "The Alchemist", "author": "Paulo Coelho", "issued": False},
    {"title": "Don Quixote", "author": "Miguel de Cervantes", "issued": False},
    {"title": "The Brothers Karamazov", "author": "Fyodor Dostoevsky", "issued": False},
    {"title": "Dracula", "author": "Bram Stoker", "issued": False},
    {"title": "Frankenstein", "author": "Mary Shelley", "issued": False},
    {"title": "A Tale of Two Cities", "author": "Charles Dickens", "issued": False},
    {"title": "The Grapes of Wrath", "author": "John Steinbeck", "issued": False},
    {"title": "Les Misérables", "author": "Victor Hugo", "issued": False},
    {"title": "The Divine Comedy", "author": "Dante Alighieri", "issued": False},
    {"title": "The Picture of Dorian Gray", "author": "Oscar Wilde", "issued": False},
    {"title": "Fahrenheit 451", "author": "Ray Bradbury", "issued": False},
    {"title": "The Sun Also Rises", "author": "Ernest Hemingway", "issued": False},
    {"title": "Gone with the Wind", "author": "Margaret Mitchell", "issued": False},
    {"title": "The Old Man and the Sea", "author": "Ernest Hemingway", "issued": False},
    {"title": "Rebecca", "author": "Daphne du Maurier", "issued": False},
    {"title": "David Copperfield", "author": "Charles Dickens", "issued": False},
    {"title": "The Scarlet Letter", "author": "Nathaniel Hawthorne", "issued": False},
    {"title": "Sense and Sensibility", "author": "Jane Austen", "issued": False},
    {"title": "Persuasion", "author": "Jane Austen", "issued": False},
    {"title": "Emma", "author": "Jane Austen", "issued": False},
    {"title": "Oliver Twist", "author": "Charles Dickens", "issued": False},
    {"title": "Treasure Island", "author": "Robert Louis Stevenson", "issued": False},
    {"title": "The Secret Garden", "author": "Frances Hodgson Burnett", "issued": False},
    {"title": "The Jungle Book", "author": "Rudyard Kipling", "issued": False},
    {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "issued": False},
    {"title": "Peter Pan", "author": "J.M. Barrie", "issued": False},
    {"title": "The Wind in the Willows", "author": "Kenneth Grahame", "issued": False},
    {"title": "Anne of Green Gables", "author": "L.M. Montgomery", "issued": False},
    {"title": "The Call of the Wild", "author": "Jack London", "issued": False},
    {"title": "White Fang", "author": "Jack London", "issued": False},
    {"title": "The Adventures of Tom Sawyer", "author": "Mark Twain", "issued": False},
    {"title": "The Adventures of Huckleberry Finn", "author": "Mark Twain", "issued": False}
]
members = [
    {"id": "M001", "name": "koba christian", "borrowed_books": []},
    {"id": "M002", "name": "roni aidoo", "borrowed_books": []},
    {"id": "M003", "name": "nathenial mensah", "borrowed_books": []},
    {"id": "M004", "name": "eleazer", "borrowed_books": []},
    {"id": "M005", "name": "snr calib", "borrowed_books": []}
]

# --- Add history tracking ---
for book in books:
    if 'history' not in book:
        book['history'] = []
for m in members:
    if 'history' not in m:
        m['history'] = []

# --- Add search/filter state ---
search_state = {"query": "", "status": ""}

# --- Audit log list ---
audit_log = []

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Librarian Login</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: url('https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1500&q=80') no-repeat center center fixed;
            background-size: cover;
        }
        .login-container {
            width: 370px;
            margin: 100px auto;
            background: rgba(255,255,255,0.95);
            padding: 35px 30px 30px 30px;
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.18);
            text-align: center;
        }
        .logo {
            width: 80px;
            margin-bottom: 15px;
            filter: drop-shadow(0 0 10px #2980b9);
        }
        h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            text-shadow: 0 0 8px #fff, 0 0 16px #2980b9;
        }
        .btn {
            padding: 8px 18px;
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 0 10px #2980b9, 0 0 20px #6dd5fa;
            transition: background 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
            background: linear-gradient(90deg, #6dd5fa, #2980b9);
            box-shadow: 0 0 20px #6dd5fa, 0 0 40px #2980b9;
        }
        .msg {
            color: #e74c3c;
            margin-bottom: 10px;
            font-weight: bold;
            text-shadow: 0 0 8px #fff;
        }
        input {
            width: 90%;
            padding: 10px;
            margin-bottom: 14px;
            border: 1px solid #2980b9;
            border-radius: 5px;
            font-size: 1em;
            box-shadow: 0 0 6px #6dd5fa;
            outline: none;
            transition: box-shadow 0.3s;
        }
        input:focus {
            box-shadow: 0 0 12px #2980b9;
        }
        .school-header {
            font-size: 1.15em;
            color: #fff;
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            padding: 10px 0 10px 0;
            border-radius: 10px 10px 0 0;
            margin-bottom: 18px;
            letter-spacing: 1px;
            font-weight: bold;
            text-shadow: 0 0 8px #2980b9, 0 0 12px #6dd5fa;
        }
        .school-logo {
            width: 60px;
            vertical-align: middle;
            margin-right: 10px;
            filter: drop-shadow(0 0 8px #fff);
        }
    </style>
</head>
<body>
<div class="login-container">
    <div class="school-header">
        <img src="{{ url_for('static', filename='f.jpg') }}" class="school-logo" alt="School Logo" style="display:block;margin:0 auto 10px auto;max-width:120px;">
        KUMASI HIGH SCHOOL<br>
        ATONSU - GYINASE, KUMASI, GHANA
    </div>
    <h2>Librarian Login</h2>
    {% if msg %}
        <div class="msg">{{ msg }}</div>
    {% endif %}
    <form method="post">
        <input name="username" placeholder="Username (mama doris)" required><br>
        <input name="password" type="password" placeholder="Password(*********)" required><br>
        <button class="btn" type="submit">Login</button>
    </form>
</div>
</body>
</html>
"""

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>KUMASI HIGH SCHOOL Library Management System</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: url('{{ wallpaper_url }}') no-repeat center center fixed;
            background-size: cover;
        }
        .container {
            width: 900px;
            margin: 40px auto;
            background: rgba(255,255,255,0.97);
            padding: 35px 40px 30px 40px;
            border-radius: 18px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.18);
            position: relative;
        }
        .logo {
            width: 70px;
            vertical-align: middle;
            margin-right: 10px;
            filter: drop-shadow(0 0 10px #2980b9);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            text-shadow: 0 0 8px #fff, 0 0 16px #2980b9;
            font-size: 2.2em;
        }
        h2 {
            color: #2980b9;
            margin-top: 30px;
            margin-bottom: 10px;
            text-shadow: 0 0 6px #fff;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.95);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 10px #6dd5fa;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 10px 8px;
            text-align: left;
        }
        th {
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            color: #fff;
            font-size: 1.1em;
        }
        .btn {
            padding: 7px 15px;
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 0 8px #2980b9, 0 0 16px #6dd5fa;
            transition: background 0.3s, box-shadow 0.3s;
        }
        .btn:hover {
            background: linear-gradient(90deg, #6dd5fa, #2980b9);
            box-shadow: 0 0 16px #6dd5fa, 0 0 32px #2980b9;
        }
        .form-inline input, .form-inline select {
            margin-right: 10px;
            padding: 7px;
            border-radius: 5px;
            border: 1px solid #2980b9;
            box-shadow: 0 0 6px #6dd5fa;
            outline: none;
            transition: box-shadow 0.3s;
        }
        .form-inline input:focus, .form-inline select:focus {
            box-shadow: 0 0 12px #2980b9;
        }
        .msg {
            color: #27ae60;
            margin-bottom: 10px;
            font-weight: bold;
            text-shadow: 0 0 8px #fff;
        }
        .danger {
            background: #e74c3c;
            box-shadow: 0 0 8px #e74c3c;
        }
        .danger:hover {
            background: #c0392b;
            box-shadow: 0 0 16px #c0392b;
        }
        .logout {
            float: right;
            margin-top: 10px;
        }
        ul {
            margin: 0;
            padding-left: 18px;
        }
        .warning {
            color: #e67e22;
            background: #fffbe6;
            border: 1px solid #e67e22;
            border-radius: 6px;
            padding: 10px 15px;
            margin-bottom: 15px;
            font-weight: bold;
            box-shadow: 0 0 10px #e67e22;
            text-align: center;
            text-shadow: 0 0 6px #fff;
        }
        .select-member {
            background: linear-gradient(90deg, #fff, #e0f7fa);
            border: 2px solid #2980b9;
            border-radius: 6px;
            padding: 7px 10px;
            color: #2980b9;
            font-weight: bold;
            box-shadow: 0 0 8px #6dd5fa;
            transition: border 0.3s, box-shadow 0.3s;
        }
        .select-member:focus {
            border: 2px solid #6dd5fa;
            box-shadow: 0 0 16px #2980b9;
        }
        .offline-link {
            display: inline-block;
            margin-bottom: 18px;
            padding: 10px 18px;
            background: linear-gradient(90deg, #6dd5fa, #2980b9);
            color: #fff;
            border-radius: 8px;
            font-weight: bold;
            text-decoration: none;
            box-shadow: 0 0 12px #2980b9;
            transition: background 0.3s, box-shadow 0.3s;
        }
        .offline-link:hover {
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            box-shadow: 0 0 24px #6dd5fa;
            color: #fff;
        }
        @media (max-width: 1000px) {
            .container { width: 98vw; padding: 10px; }
            table, th, td { font-size: 0.95em; }
        }
        .school-header {
            font-size: 1.25em;
            color: #fff;
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            padding: 12px 0 12px 0;
            border-radius: 12px 12px 0 0;
            margin-bottom: 22px;
            letter-spacing: 1.5px;
            font-weight: bold;
            text-align: center;
            text-shadow: 0 0 10px #2980b9, 0 0 18px #6dd5fa;
        }
        .school-logo {
            width: 70px;
            vertical-align: middle;
            margin-right: 12px;
            filter: drop-shadow(0 0 10px #fff);
        }
        .profile-btn, .settings-btn {
            float: right;
            margin-top: 10px;
            margin-right: 10px;
            padding: 7px 15px;
            background: linear-gradient(90deg, #6dd5fa, #2980b9);
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 0 8px #2980b9, 0 0 16px #6dd5fa;
            transition: background 0.3s, box-shadow 0.3s;
            text-decoration: none;
        }
        .profile-btn:hover, .settings-btn:hover {
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            box-shadow: 0 0 16px #6dd5fa, 0 0 32px #2980b9;
        }
        .profile-pic-small {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid #2980b9;
            margin-right: 8px;
            vertical-align: middle;
            box-shadow: 0 0 8px #6dd5fa;
        }
        .settings-icon {
            width: 22px;
            height: 22px;
            vertical-align: middle;
            margin-right: 6px;
            filter: drop-shadow(0 0 4px #6dd5fa);
        }
        .footer-copyright {
            margin-top: 40px;
            text-align: center;
            color: #2980b9;
            font-size: 1.05em;
            opacity: 0.85;
            letter-spacing: 0.04em;
            font-weight: bold;
            text-shadow: 0 0 8px #fff;
        }
        .history-table { margin-top:16px; }
        .history-table th,.history-table td { font-size:0.97em; }
        .import-export-btn { margin: 5px 8px 5px 0; padding:6px 14px; }
        .overdue { background: #ffeaea !important; color: #c0392b !important; font-weight:bold; }
        .search-bar { margin-bottom: 18px; }
        .modal-bg { display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.45); z-index:9999; }
        .modal-content { background:#fff; border-radius:12px; max-width:420px; margin:80px auto; padding:0; box-shadow:0 0 24px #2980b9; }
        .modal-close { float:right; font-size:1.5em; color:#c0392b; cursor:pointer; margin:8px 12px 0 0; }
    </style>
    <script>
    // Book Details Modal JS
    function showBookDetails(idx) {
        var modalBg = document.getElementById('modal-bg');
        var modalContent = document.getElementById('modal-content');
        modalContent.innerHTML = '<div style="padding:32px;text-align:center;">Loading...</div>';
        modalBg.style.display = 'block';
        fetch('/book_details/' + idx)
            .then(resp => resp.text())
            .then(html => { modalContent.innerHTML = '<span class="modal-close" onclick="closeModal()">&times;</span>' + html; });
    }
    function closeModal() {
        document.getElementById('modal-bg').style.display = 'none';
    }
    </script>
</head>
<body style="background: url('{{ wallpaper_url }}') no-repeat center center fixed; background-size: cover;">
<div class="container">
    <div class="school-header">
        <img src="{{ url_for('static', filename='kuhis.jpg') }}" class="school-logo" alt="School Logo" style="vertical-align:middle; margin-right:12px;">
        KUMASI HIGH SCHOOL &nbsp;|&nbsp; ATONSU - GYINASE, KUMASI, GHANA
        <div style="margin-top:10px; font-size:1.3em; color:#2980b9; font-weight:bold; letter-spacing:0.07em; text-shadow:0 0 8px #fff;">
            WE ARE COMING !!!  ARISE KUHIS
        </div>
    </div>
    <form method="post" action="/logout" style="float:right;">
        <button class="btn logout" type="submit">Logout</button>
    </form>
    <!-- Profile Button -->
    <a href="{{ url_for('profile') }}" class="profile-btn" style="float:right; margin-top:10px; margin-right:10px; padding:7px 15px; background:linear-gradient(90deg, #6dd5fa, #2980b9); color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:bold; box-shadow:0 0 8px #2980b9, 0 0 16px #6dd5fa; text-decoration:none;">
        <img src="{{ profile_pic_url }}" class="profile-pic-small" alt="Profile" style="width:38px; height:38px; border-radius:50%; object-fit:cover; border:2px solid #2980b9; margin-right:8px; vertical-align:middle; box-shadow:0 0 8px #6dd5fa;">
        Profile
    </a>
    <!-- Librarian Info -->
    <div style="clear:both; margin-bottom:10px; text-align:right;">
        <span style="color:#2980b9; font-weight:bold;">Librarian: {{ librarian_name }}</span><br>
        <span style="color:#888; font-size:0.95em;">Password: {{ librarian_password }}</span>
    </div>
    <img src="kuhis.jpg" class="logo" alt="Library Logo">
    <h1>Library Management System</h1>
    <a class="offline-link" href="/download_software" download>
        &#128187; Download Offline Library Software
    </a>
    <div style="color:#e67e22; margin-top:8px; font-weight:bold;">
        After download, open the file to launch the offline library.
    </div>
    <!-- Search/Filter Form -->
    <form method="get" action="/" class="search-bar">
        <input name="q" placeholder="Search title or author" value="{{ search_query|default('') }}" style="padding:7px; border-radius:5px; border:1px solid #2980b9;">
        <select name="status" style="padding:7px; border-radius:5px; border:1px solid #2980b9;">
            <option value="">All Status</option>
            <option value="available" {% if search_status=='available' %}selected{% endif %}>Available</option>
            <option value="issued" {% if search_status=='issued' %}selected{% endif %}>Issued</option>
            <option value="overdue" {% if search_status=='overdue' %}selected{% endif %}>Overdue</option>
        </select>
        <button class="btn" type="submit">Search</button>
        {% if search_query or search_status %}
        <a href="{{ url_for('home') }}" class="btn danger" style="margin-left:10px;">Clear</a>
        {% endif %}
    </form>
    <!-- Export/Import Buttons -->
    <form style="display:inline;" method="get" action="/export_books">
        <button class="btn import-export-btn" type="submit">&#128190; Export Books (CSV)</button>
    </form>
    <form style="display:inline;" method="get" action="/export_members">
        <button class="btn import-export-btn" type="submit">&#128190; Export Members (CSV)</button>
    </form>
    <form style="display:inline;" method="post" action="/import_books" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv" required style="padding:0;max-width:130px;">
        <button class="btn import-export-btn" type="submit">&#128228; Import Books</button>
    </form>
    <form style="display:inline;" method="post" action="/import_members" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv" required style="padding:0;max-width:130px;">
        <button class="btn import-export-btn" type="submit">&#128228; Import Members</button>
    </form>
    {% if msg %}
        <div class="msg">{{ msg }}</div>
        {% if "returned" in msg|lower %}
        <script>
        // Speech synthesis for book return
        var memberName = {{ returned_member_name|tojson if returned_member_name else "null" }};
        if ('speechSynthesis' in window && memberName) {
            var utter = new SpeechSynthesisUtterance("Thank you my dear " + memberName + ", learn hard");
            utter.rate = 1.0;
            utter.pitch = 1.0;
            window.speechSynthesis.speak(utter);
        }
        </script>
        {% endif %}
    {% endif %}
    {% if warning %}
        <div class="warning">{{ warning }}</div>
    {% endif %}
    <h2>Books</h2>
    <table>
        <tr><th>#</th><th>Title</th><th>Author</th><th>Status</th><th>Actions</th></tr>
        {% for book in books %}
        {% set overdue = (book.issued and book.due_date and get_remaining_time(book.due_date) == "Overdue!") %}
        <tr {% if overdue %}class="overdue"{% endif %}>
            <td>{{ loop.index }}</td>
            <td>
                <a href="javascript:void(0);" onclick="showBookDetails({{ loop.index0 }})" style="color:#2980b9;text-decoration:underline;">
                    {{ book.title }}
                </a>
            </td>
            <td>{{ book.author }}</td>
            <td>
                {% if book.issued %}
                    Issued
                    {% if book.due_date %}
                        <br>
                        <span style="color:#e67e22;font-weight:bold;">
                            ⏳ {{ get_remaining_time(book.due_date) }}
                        </span>
                    {% endif %}
                {% else %}
                    Available
                {% endif %}
            </td>
            <td>
                {% if not book.issued %}
                <form method="post" action="/borrow" style="display:inline;">
                    <input type="hidden" name="book_idx" value="{{ loop.index0 }}">
                    <select name="member_id" class="select-member" required>
                        <option value="">&#9733; Select Member &#9733;</option>
                        {% for m in members %}
                        <option value="{{ m.id }}">{{ m.name }} ({{ m.id }})</option>
                        {% endfor %}
                    </select>
                    <button class="btn" type="submit">Borrow</button>
                </form>
                {% else %}
                <form method="post" action="/return" style="display:inline;">
                    <input type="hidden" name="book_idx" value="{{ loop.index0 }}">
                    <button class="btn" type="submit">Return</button>
                </form>
                {% endif %}
                <form method="post" action="/remove_book" style="display:inline;">
                    <input type="hidden" name="book_idx" value="{{ loop.index0 }}">
                    <button class="btn danger" type="submit" onclick="return confirm('Remove this book?');">Remove</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
    <form method="post" action="/add_book" class="form-inline">
        <input name="title" placeholder="Book Title" required>
        <input name="author" placeholder="Author" required>
        <button class="btn" type="submit">Add Book</button>
    </form>
    <!-- --- Book Borrow/Return History Table --- -->
    <h2>Borrow/Return History</h2>
    <table class="history-table" border="1" width="100%">
        <tr><th>Book</th><th>Action</th><th>Member</th><th>Date &amp; Time</th></tr>
        {% for item in global_history|reverse %}
            <tr>
                <td>{{ item.book }}</td>
                <td>{{ item.action }}</td>
                <td>{{ item.member }}</td>
                <td>{{ item.timestamp }}</td>
            </tr>
        {% endfor %}
    </table>
    <h2>Audit Log</h2>
    <table class="history-table" border="1" width="100%">
        <tr><th>Action</th><th>Detail</th><th>Date &amp; Time</th></tr>
        {% for log in audit_log|reverse %}
            <tr>
                <td>{{ log.action }}</td>
                <td>{{ log.detail }}</td>
                <td>{{ log.timestamp }}</td>
            </tr>
        {% endfor %}
    </table>
    <h2>Members</h2>
    <table>
        <tr><th>ID</th><th>Name</th><th>Borrowed Books</th></tr>
        {% for m in members %}
        <tr>
            <td>{{ m.id }}</td>
            <td>{{ m.name }}</td>
            <td>
                {% if m.borrowed_books %}
                    <ul>
                    {% for b in m.borrowed_books %}
                        <li>{{ b }}</li>
                    {% endfor %}
                    </ul>
                {% else %}
                    0
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
    <form method="post" action="/add_member" class="form-inline">
        <input name="name" placeholder="Member Name" required>
        <button class="btn" type="submit">Add Member</button>
    </form>
    <div class="footer-copyright">
        &copy; 2025 Kumasi High School Library Management. All rights reserved.
        done by STEM NOBOTICS GROUP@25
    </div>
    <!-- Modal for Book Details -->
    <div id="modal-bg" class="modal-bg" onclick="closeModal()">
        <div id="modal-content" class="modal-content" onclick="event.stopPropagation();"></div>
    </div>
</div>
</body>
</html>
"""

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

SCHOOL_LOGO = "kuhis.jpg"
LIBRARY_LOGO = "f.jpg"
DEFAULT_WALLPAPER = "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1500&q=80"

# Remove duplicate/unused logo/profile variables
profile_settings = {
    "profile_pic": None,
    "wallpaper": None,
    "school_logo": SCHOOL_LOGO,
    "library_logo": LIBRARY_LOGO
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, file_type):
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        new_filename = f"{file_type}_{int(time.time())}.{ext}"
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            
        filepath = os.path.join(UPLOAD_FOLDER, new_filename)
        file.save(filepath)
        return new_filename
    return None

def get_file_url(file_type):
    if profile_settings[file_type]:
        path = os.path.join(UPLOAD_FOLDER, profile_settings[file_type])
        if os.path.exists(path):
            return url_for('static', filename=f'uploads/{profile_settings[file_type]}')
    
    # Default fallbacks
    if file_type == "profile_pic":
        return url_for('static', filename=SCHOOL_LOGO)
    elif file_type == "wallpaper":
        return DEFAULT_WALLPAPER
    elif file_type == "school_logo":
        return url_for('static', filename=SCHOOL_LOGO)
    else:  # library_logo
        return url_for('static', filename=LIBRARY_LOGO)

PROFILE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Profile & Settings</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: url('{{ wallpaper_url }}') no-repeat center center fixed;
            background-size: cover;
        }
        .profile-container {
                    width: 440px;
            margin: 60px auto;
            background: rgba(255,255,255,0.97);
            padding: 32px 28px 28px 28px;
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            text-align: center;
        }
        .profile-pic {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            object-fit: cover;
            border: 4px solid #2980b9;
            margin-bottom: 18px;
            box-shadow: 0 0 18px #6dd5fa;
        }
        h2 {
            color: #2c3e50;
            margin-bottom: 18px;
        }
        .btn {
            padding: 8px 18px;
            background: linear-gradient(90deg, #2980b9, #6dd5fa);
            color: #fff;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
        }
        .btn:hover {
            background: linear-gradient(90deg, #6dd5fa, #2980b9);
        }
        .back-link {
            display: inline-block;
            margin-top: 18px;
            color: #2980b9;
            text-decoration: underline;
            font-weight: bold;
        }
        .setting-section {
            margin-bottom: 28px;
        }
        label {
            font-weight: bold;
            color: #2980b9;
        }
        input[type="file"] {
            margin-top: 8px;
        }
        .msg {
            color: #27ae60;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .settings-title {
            font-size: 1.1em;
            color: #2980b9;
            margin-bottom: 8px;
            font-weight: bold;
        }
        .settings-list {
            text-align: left;
            margin: 0 auto 18px auto;
            padding: 0 0 0 18px;
            color: #222;
        }
        .settings-list li {
            margin-bottom: 7px;
        }
        .divider {
            border-bottom: 1px solid #e0e0e0;
            margin: 18px 0;
        }
        .footer-copyright {
            margin-top: 40px;
            text-align: center;
            color: #2980b9;
            font-size: 1.05em;
            opacity: 0.85;
            letter-spacing: 0.04em;
            font-weight: bold;
            text-shadow: 0 0 8px #fff;
        }
        .pw-section { margin-top:30px; padding:18px 0 0 0; border-top:1px solid #e0e0e0; }
        .pw-label { font-weight:bold; color:#2980b9; }
        .pw-input { margin-bottom:10px; padding:7px; border-radius:5px; border:1px solid #2980b9; width:90%; }
    </style>
</head>
<body>
<div class="profile-container">
    <h2>Profile & Settings</h2>
    {% if msg %}
        <div class="msg">{{ msg }}</div>
    {% endif %}
    <div class="setting-section">
        <label>Profile Picture:</label><br>
        <img src="{{ profile_pic_url }}" class="profile-pic" alt="Profile Picture"><br>
        <form method="post" enctype="multipart/form-data" style="margin-top:10px;">
            <input type="file" name="profile_pic" accept="image/*" required>
            <button class="btn" type="submit" name="action" value="profile_pic">Change Picture</button>
        </form>
    </div>
    <div class="setting-section">
        <label>Wallpaper:</label><br>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="wallpaper" accept="image/*" required>
            <button class="btn" type="submit" name="action" value="wallpaper">Change Wallpaper</button>
        </form>
    </div>
    <div class="pw-section">
        <form method="post" action="/change_password">
            <div class="pw-label">Change Password:</div>
            <input class="pw-input" type="password" name="old_password" placeholder="Old Password" required><br>
            <input class="pw-input" type="password" name="new_password" placeholder="New Password" required><br>
            <input class="pw-input" type="password" name="confirm_password" placeholder="Confirm New Password" required><br>
            <button class="btn" type="submit">Change Password</button>
        </form>
    </div>
    <div class="divider"></div>
    <div class="setting-section">
        <div class="settings-title">Library Management Settings</div>
        <ul class="settings-list">
            <li>Change your profile picture (above)</li>
            <li>Change your library wallpaper (above)</li>
            <li>All changes are saved instantly for your session</li>
            <li>More settings can be added here as needed</li>
        </ul>
    </div>
    <a href="{{ url_for('home') }}" class="back-link">&#8592; Back to Library</a>
    <div class="footer-copyright">
        &copy; 2025 Kumasi High School Library Management. All rights reserved.
    </div>
</div>
</body>
</html>
"""

SETTINGS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Library Settings</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: url('{{ wallpaper_url }}') no-repeat center center fixed;
            background-size: cover;
        }
        .settings-container {
            width: 440px;
            margin: 60px auto;
            background: rgba(255,255,255,0.97);
            padding: 32px 28px 28px 28px;
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            text-align: center;
        }
        h2 {
            color: #2c3e50;
            margin-bottom: 18px;
        }
        .settings-title {
            font-size: 1.1em;
            color: #2980b9;
            margin-bottom: 8px;
            font-weight: bold;
        }
        .settings-list {
            text-align: left;
            margin: 0 auto 18px auto;
            padding: 0 0 0 18px;
            color: #222;
        }
        .settings-list li {
            margin-bottom: 7px;
        }
        .back-link {
            display: inline-block;
            margin-top: 18px;
            color: #2980b9;
            text-decoration: underline;
            font-weight: bold;
        }
        .footer-copyright {
            margin-top: 40px;
            text-align: center;
            color: #2980b9;
            font-size: 1.05em;
            opacity: 0.85;
            letter-spacing: 0.04em;
            font-weight: bold;
            text-shadow: 0 0 8px #fff;
        }
    </style>
</head>
<body>
<div class="settings-container">
    <h2>Library Management Settings</h2>
    <div class="settings-title">Available Settings</div>
    <ul class="settings-list">
        <li>Change your profile picture (see Profile page)</li>
        <li>Change your library wallpaper (see Profile page)</li>
        <li>All changes are saved instantly for your session</li>
        <li>More settings can be added here as needed</li>
    </ul>
    <a href="{{ url_for('home') }}" class="back-link">&#8592; Back to Library</a>
    <div class="footer-copyright">
        &copy; 2025 Kumasi High School Library Management. All rights reserved.
        done by STEM NOBOTICS GROUP@25..
    </div>
</div>
</body>
</html>
"""

# --- Global Borrow/Return History List ---
global_history = []

def is_logged_in():
    return session.get("logged_in", False)

@app.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("home"))
    msg = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == LIBRARIAN_USERNAME and password == LIBRARIAN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            msg = "Invalid username or password."
    return render_template_string(LOGIN_TEMPLATE, msg=msg)

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/", methods=["GET"])
def home():
    if not is_logged_in():
        return redirect(url_for("login"))
    # --- Search/filter logic ---
    q = request.args.get("q", "").strip().lower()
    status = request.args.get("status", "")
    filtered_books = books
    if q:
        filtered_books = [b for b in filtered_books if q in b["title"].lower() or q in b["author"].lower()]
    if status == "available":
        filtered_books = [b for b in filtered_books if not b.get("issued")]
    elif status == "issued":
        filtered_books = [b for b in filtered_books if b.get("issued")]
    elif status == "overdue":
        filtered_books = [
            b for b in filtered_books
            if b.get("issued") and b.get("due_date") and get_remaining_time(b["due_date"]) == "Overdue!"
        ]
    return render_template_string(
        TEMPLATE,
        **get_template_vars(books=filtered_books, search_query=q, search_status=status)
    )

@app.route("/add_book", methods=["POST"])
def add_book():
    if not is_logged_in():
        return redirect(url_for("login"))
    title = request.form["title"]
    author = request.form["author"]
    books.append({"title": title, "author": author, "issued": False, "history": []})
    msg = f"Book '{title}' added."
    # --- Audit log ---
    audit_log.append({
        "action": "Add Book",
        "detail": f"Added '{title}' by {author}",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return render_template_string(TEMPLATE, **get_template_vars(msg=msg))

@app.route("/remove_book", methods=["POST"])
def remove_book():
    if not is_logged_in():
        return redirect(url_for("login"))
    idx = int(request.form["book_idx"])
    book = books.pop(idx)
    for m in members:
        if book["title"] in m["borrowed_books"]:
            m["borrowed_books"].remove(book["title"])
    msg = f"Book '{book['title']}' removed."
    # --- Audit log ---
    audit_log.append({
        "action": "Remove Book",
        "detail": f"Removed '{book['title']}'",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return render_template_string(TEMPLATE, **get_template_vars(msg=msg))

@app.route("/add_member", methods=["POST"])
def add_member():
    if not is_logged_in():
        return redirect(url_for("login"))
    name = request.form["name"]
    member_id = f"M{len(members)+1:03d}"
    members.append({"id": member_id, "name": name, "borrowed_books": [], "history": []})
    msg = f"Member '{name}' added."
    # --- Audit log ---
    audit_log.append({
        "action": "Add Member",
        "detail": f"Added member '{name}' ({member_id})",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return render_template_string(TEMPLATE, **get_template_vars(msg=msg))

# Add a due_date field to each book when borrowed
@app.route("/borrow", methods=["POST"])
def borrow():
    if not is_logged_in():
        return redirect(url_for("login"))
    book_idx = int(request.form["book_idx"])
    member_id = request.form["member_id"]
    book = books[book_idx]
    warning = None
    due_date = None
    if book.get("issued"):
        msg = "Book already issued."
    else:
        member = next((m for m in members if m["id"] == member_id), None)
        if member:
            book["issued"] = True
            member["borrowed_books"].append(book["title"])
            # Set due date to 3 days from now
            due_date = datetime.datetime.now() + datetime.timedelta(days=3)
            book["due_date"] = due_date.strftime("%Y-%m-%d %H:%M:%S")
            # --- Record event in history ---
            event = {
                "book": book["title"],
                "action": "Borrowed",
                "member": member["name"],
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            book.setdefault("history", []).append(event)
            member.setdefault("history", []).append(event)
            global_history.append(event)
            msg = f"Book '{book['title']}' issued to {member['name']}."
            warning = "⚠️ Please return this book within 3 days, or at most 1 week, to avoid penalties!"
            # --- Audit log ---
            audit_log.append({
                "action": "Borrow Book",
                "detail": f"Issued '{book['title']}' to {member['name']} ({member['id']})",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            msg = "Member not found."
    return render_template_string(TEMPLATE, **get_template_vars(msg=msg, warning=warning))

# Remove due_date when returned
@app.route("/return", methods=["POST"])
def return_book():
    if not is_logged_in():
        return redirect(url_for("login"))
    book_idx = int(request.form["book_idx"])
    book = books[book_idx]
    warning = None
    returned_member_name = None
    if not book["issued"]:
        msg = "Book is not issued."
    else:
        for m in members:
            if book["title"] in m["borrowed_books"]:
                m["borrowed_books"].remove(book["title"])
                returned_member_name = m["name"]
                # --- Record event in history ---
                event = {
                    "book": book["title"],
                    "action": "Returned",
                    "member": m["name"],
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                book.setdefault("history", []).append(event)
                m.setdefault("history", []).append(event)
                global_history.append(event)
                # --- Audit log ---
                audit_log.append({
                    "action": "Return Book",
                    "detail": f"Returned '{book['title']}' by {m['name']} ({m['id']})",
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                break
        book["issued"] = False
        if "due_date" in book:
            del book["due_date"]
        msg = f"Book '{book['title']}' returned."
    return render_template_string(
        TEMPLATE,
        **get_template_vars(msg=msg, warning=warning),
        returned_member_name=returned_member_name
    )

# Helper to get remaining time for a book
def get_remaining_time(due_date_str):
    try:
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        delta = due_date - now
        if delta.total_seconds() < 0:
            return "Overdue!"
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m left"
    except Exception:
        return ""

# Pass get_remaining_time to the template
def get_template_vars(msg=None, warning=None, books=None, search_query=None, search_status=None):
    return {
        "books": books if books is not None else globals()["books"],
        "members": members,
        "msg": msg,
        "warning": warning,
        "profile_pic_url": get_file_url("profile_pic"),
        "wallpaper_url": get_file_url("wallpaper"),
        "school_logo_url": get_file_url("school_logo"),
        "library_logo_url": get_file_url("library_logo"),
        "librarian_name": LIBRARIAN_USERNAME,
        "librarian_password": LIBRARIAN_PASSWORD,
        "get_remaining_time": get_remaining_time,
        "global_history": global_history,
        "search_query": search_query,
        "search_status": search_status,
        "audit_log": audit_log,
    }

@app.route("/download_software")
def download_software():
    # Serve the GUI version of library_management.py
    import os
    file_path = os.path.join(os.path.dirname(__file__), "library_management.py")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "<h2 style='color:red;text-align:center;margin-top:40px;'>Offline software not found. Please ensure <b>library_management.py</b> (the GUI version) is in the same folder as your website.</h2>", 404

@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Simple profile page for changing profile picture
    msg = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "profile_pic":
            file = request.files.get("profile_pic")
            if not file or file.filename == "":
                msg = "No file selected. Please choose an image."
            elif not allowed_file(file.filename):
                msg = "Invalid file type. Please select PNG, JPG, JPEG, or GIF."
            else:
                if not os.path.exists(UPLOAD_FOLDER):
                    os.makedirs(UPLOAD_FOLDER)
                try:
                    new_filename = save_uploaded_file(file, "profile_pic")
                    if new_filename:
                        profile_settings["profile_pic"] = new_filename
                        msg = "Profile picture updated successfully!"
                    else:
                        msg = "File upload failed. Please try again."
                except Exception as e:
                    msg = f"Error saving file: {e}"
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Librarian Profile</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #f4f8fb; }
            .profile-container { width: 400px; margin: 60px auto; background: #fff; padding: 32px 28px 28px 28px; border-radius: 16px; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.13); text-align: center; }
            .profile-pic { width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 4px solid #2980b9; margin-bottom: 18px; box-shadow: 0 0 18px #6dd5fa; }
            h2 { color: #2c3e50; margin-bottom: 18px; }
            .btn { padding: 8px 18px; background: linear-gradient(90deg, #2980b9, #6dd5fa); color: #fff; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 10px; }
            .btn:hover { background: linear-gradient(90deg, #6dd5fa, #2980b9); }
            .back-link { display: inline-block; margin-top: 18px; color: #2980b9; text-decoration: underline; font-weight: bold; }
            .msg { color: #27ae60; margin-bottom: 10px; font-weight: bold; }
            .librarian-info { margin-top: 16px; color: #2980b9; font-weight: bold; }
            .librarian-pass { color: #888; font-size: 0.95em; }
        </style>
    </head>
    <body>
    <div class="profile-container">
        <h2>Librarian Profile</h2>
        {% if msg %}
            <div class="msg">{{ msg }}</div>
        {% endif %}
        <img src="{{ profile_pic_url }}" class="profile-pic" alt="Profile Picture"><br>
        <form method="post" enctype="multipart/form-data" style="margin-top:10px;">
            <input type="file" name="profile_pic" accept="image/*" required>
            <button class="btn" type="submit" name="action" value="profile_pic">Change Picture</button>
        </form>
        <div class="librarian-info">
            Librarian: {{ librarian_name }}<br>
            <span class="librarian-pass">Password: {{ librarian_password }}</span>
        </div>
        <a href="{{ url_for('home') }}" class="back-link">&#8592; Back to Library</a>
    </div>
    </body>
    </html>
    """,
    profile_pic_url=get_file_url("profile_pic"),
    msg=msg,
    librarian_name=LIBRARIAN_USERNAME,
    librarian_password=LIBRARIAN_PASSWORD
    )

@app.route("/settings", methods=["GET"])
def settings():
    if not is_logged_in():
        return redirect(url_for("login"))
    wallpaper_url = get_file_url("wallpaper")
    return render_template_string(SETTINGS_TEMPLATE, wallpaper_url=wallpaper_url)

# --- Export/Import Book/Member CSV ---
@app.route("/export_books", methods=["GET"])
def export_books():
    if not is_logged_in():
        return redirect(url_for("login"))
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['title', 'author', 'issued'])
    for b in books:
        writer.writerow([b["title"], b["author"], b["issued"]])
    output = si.getvalue()
    return (output, 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment;filename=books_export.csv"
    })

@app.route("/export_members", methods=["GET"])
def export_members():
    if not is_logged_in():
        return redirect(url_for("login"))
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['id', 'name'])
    for m in members:
        writer.writerow([m["id"], m["name"]])
    output = si.getvalue()
    return (output, 200, {
        "Content-Type": "text/csv",
        "Content-Disposition": "attachment;filename=members_export.csv"
    })

@app.route("/import_books", methods=["POST"])
def import_books():
    if not is_logged_in():
        return redirect(url_for("login"))
    file = request.files.get("file")
    if not file: return render_template_string(TEMPLATE, **get_template_vars(msg="No file selected!"))
    try:
        content = file.read().decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        books.clear()
        for row in reader:
            books.append({
                "title": row.get("title", ""),
                "author": row.get("author", ""),
                "issued": row.get("issued", "False") == "True",
                "history": []
            })
        msg = "Books imported successfully."
    except Exception as e:
        msg = f"Import failed: {e}"
    return render_template_string(TEMPLATE, **get_template_vars(msg=msg))

@app.route("/import_members", methods=["POST"])
def import_members():
    if not is_logged_in():
        return redirect(url_for("login"))
    file = request.files.get("file")
    if not file: return render_template_string(TEMPLATE, **get_template_vars(msg="No file selected!"))
    try:
        content = file.read().decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        members.clear()
        for row in reader:
            members.append({
                "id": row.get("id", ""),
                "name": row.get("name", ""),
                "borrowed_books": [],
                "history": []
            })
        msg = "Members imported successfully."
    except Exception as e:
        msg = f"Import failed: {e}"
    return render_template_string(TEMPLATE, **get_template_vars(msg=msg))

# --- Change Password Functionality ---
@app.route("/change_password", methods=["POST"])
def change_password():
    if not is_logged_in():
        return redirect(url_for("login"))
    old = request.form.get("old_password")
    new = request.form.get("new_password")
    confirm = request.form.get("confirm_password")
    global LIBRARIAN_PASSWORD
    msg = None
    if old != LIBRARIAN_PASSWORD:
        msg = "Old password incorrect."
    elif not new or new != confirm:
        msg = "New passwords do not match."
    else:
        LIBRARIAN_PASSWORD = new
        msg = "Password changed successfully."
    return render_template_string(PROFILE_TEMPLATE, 
        profile_pic_url=get_file_url("profile_pic"),
        msg=msg,
        librarian_name=LIBRARIAN_USERNAME,
        librarian_password=LIBRARIAN_PASSWORD,
        wallpaper_url=get_file_url("wallpaper")
    )

# --- Book Details Modal Functionality ---
# Add a route to show book details (AJAX-style, returns HTML snippet)
@app.route("/book_details/<int:book_idx>")
def book_details(book_idx):
    if not is_logged_in():
        return "Not authorized", 403
    if book_idx < 0 or book_idx >= len(books):
        return "Book not found", 404
    book = books[book_idx]
    history = book.get("history", [])
    return render_template_string("""
    <div style="padding:18px;">
        <h3>{{ book.title }}</h3>
        <p><b>Author:</b> {{ book.author }}</p>
        <p><b>Status:</b> {% if book.issued %}Issued{% else %}Available{% endif %}</p>
        {% if book.due_date %}
        <p><b>Due Date:</b> {{ book.due_date }}</p>
        {% endif %}
        <h4>History</h4>
        <ul>
        {% for h in history|reverse %}
            <li>{{ h.action }} by {{ h.member }} at {{ h.timestamp }}</li>
        {% else %}
            <li>No history yet.</li>
        {% endfor %}
        </ul>
    </div>
    """, book=book, history=history)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host="127.0.1.1", port=5000, debug=False)
