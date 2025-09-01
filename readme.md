# 📚 Library Management System

A powerful and user-friendly desktop application for managing library operations.
Built with **Python**, **PyQt5**, and **MySQL/SQLite**, this system enables librarians to manage books, members, and transactions efficiently — with **real-time analytics** and a **modern UI**.

---

## 🚀 Features

- 🔐 **User Authentication**
  Secure login system backed by MySQL.

- 📖 **Book Management**
  Add, update, and remove books. Track genres, authors, ISBNs, and available copies.

- 👤 **Member Management**
  Register and manage members with detailed profiles and membership plans.

- 🔁 **Transactions**
  Issue and return books with automatic due-date tracking and overdue handling.

- 📊 **Interactive Dashboard**
  See library stats like total books, active loans, overdue items, and recent activities.

- 📈 **Data Visualizations**
  - 📊 Bar chart: Monthly checkouts vs. returns
  - 🥧 Pie chart: Top 5 book genres
  - 📈 Line chart: Peak borrowing hours
  - 🌡 Heatmap: Busiest library sections

---

## 🛠️ Tech Stack

| Layer         | Technology                                        |
| ------------- | ------------------------------------------------- |
| **Frontend**  | Python, PyQt5                                     |
| **Backend**   | MySQL / SQLite                                    |
| **GUI Tools** | Qt Designer                                       |
| **Data Viz**  | Matplotlib, Plotly, PyQtGraph, Seaborn (optional) |

---

## 📁 Project Structure

```bash
library_system/
│── main.py
│
├── db/
│   ├── database.py          # DB connection manager
│   ├── models.py            # ORM models (User, Patron, Books, Payments, etc.)
│   └── init_db.py           # Initial DB setup
│
├── controllers/
│   ├── auth_controller.py   # Authentication logic
│   ├── users_controller.py
│   ├── payments_controller.py
│   └── books_controller.py
│
├── ui/
│   ├── main_window.py       # Main dashboard
│   ├── login_window.py      # Login screen
│   ├── users_view.py
│   └── ...
│
└── utils/
    └── security.py          # Password hashing (bcrypt/argon2)
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repo

```bash
git clone https://github.com/TJselevani/LibraryMGMT.git
cd LibraryMGMT
```

### 2️⃣ Create a virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up the database

For MySQL, run:

```bash
python setup.py
```

This will create tables and insert sample data.
This will create default user "admin" and password "password123"

### 5️⃣ Run the app

This will create default user "admin" and password "admin123" if you did not run the setup.py command

```bash
python main.py
```

---

## 🧪 Screenshots

Coming soon...
(You can add screenshots of your **login page**, **dashboard**, and **charts** here.)

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss what you would like to change.

---

## 📬 Contact

👨‍💻 Developed by **TJ selevani**
📧 Email: [tjselevani@gmail.com](mailto:tjselevani@gmail.com)
🌐 GitHub: [TJselevani](https://github.com/TJselevani)
