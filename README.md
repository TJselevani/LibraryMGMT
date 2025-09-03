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
LibraryMGMT/
│
├── main.py                          # Application entry point
├── requirements.txt                 # Dependencies
├── README.md                       # Project documentation
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
│
├── app/                            # Main application package
│   ├── __init__.py
│   ├── application.py              # Application bootstrap and setup
│   └── main_window.py             # Refactored main window
│
├── core/                          # Core business logic and patterns
│   ├── __init__.py
│   ├── base/                      # Base classes and interfaces
│   │   ├── __init__.py
│   │   ├── controller.py          # Base controller class
│   │   ├── repository.py          # Base repository pattern
│   │   └── service.py             # Base service class
│   │
│   ├── patterns/                  # Design pattern implementations
│   │   ├── __init__.py
│   │   ├── command.py             # Command pattern
│   │   ├── factory.py             # Factory patterns
│   │   ├── observer.py            # Observer pattern
│   │   ├── singleton.py           # Singleton pattern
│   │   └── strategy.py            # Strategy pattern
│   │
│   └── exceptions/                # Custom exceptions
│       ├── __init__.py
│       ├── base.py                # Base exception classes
│       ├── validation.py          # Validation exceptions
│       └── database.py            # Database exceptions
│
├── infrastructure/                # External concerns and frameworks
│   ├── __init__.py
│   ├── database/                  # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py          # Database connection management
│   │   ├── migrations/            # Database migrations
│   │   │   ├── __init__.py
│   │   │   └── versions/          # Migration files
│   │   └── repositories/          # Data access layer
│   │       ├── __init__.py
│   │       ├── base_repository.py
│   │       ├── user_repository.py
│   │       ├── patron_repository.py
│   │       ├── book_repository.py
│   │       ├── borrowed_book_repository.py
│   │       └── payment_repository.py
│   │
│   ├── external/                  # External service integrations
│   │   ├── __init__.py
│   │   ├── email_service.py       # Email notifications
│   │   └── sms_service.py         # SMS notifications
│   │
│   └── logging/                   # Logging configuration
│       ├── __init__.py
│       ├── handlers.py            # Custom log handlers
│       └── formatters.py          # Log formatters
│
├── domain/                        # Domain models and business rules
│   ├── __init__.py
│   ├── models/                    # Domain models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── patron.py
│   │   ├── book.py
│   │   ├── borrowed_book.py
│   │   └── payment.py
│   │
│   ├── entities/                  # Business entities
│   │   ├── __init__.py
│   │   ├── library_member.py
│   │   ├── library_item.py
│   │   └── transaction.py
│   │
│   └── value_objects/             # Value objects
│       ├── __init__.py
│       ├── money.py
│       ├── date_range.py
│       └── contact_info.py
│
├── services/                      # Application services
│   ├── __init__.py
│   ├── auth_service.py            # Authentication service
│   ├── navigation_service.py      # Navigation management
│   ├── data_service.py            # Data operations
│   ├── notification_service.py    # Notifications
│   ├── export_service.py          # Data export
│   ├── import_service.py          # Data import
│   └── library_service.py         # Core library operations
│
├── managers/                      # System managers
│   ├── __init__.py
│   ├── session_manager.py         # Session management
│   ├── cache_manager.py           # Caching layer
│   ├── config_manager.py          # Configuration management
│   └── plugin_manager.py          # Plugin system
│
├── controllers/                   # Application controllers (existing)
│   ├── __init__.py
│   ├── base_controller.py         # Base controller
│   ├── users_controller.py
│   ├── patrons_controller.py
│   ├── books_controller.py
│   ├── borrowed_books_controller.py
│   └── payments_controller.py
│
├── ui/                           # User interface layer
│   ├── __init__.py
│   ├── factories/                # UI factories
│   │   ├── __init__.py
│   │   ├── view_factory.py
│   │   ├── form_factory.py
│   │   └── dialog_factory.py
│   │
│   ├── screens/                  # Main screens/views
│   │   ├── __init__.py
│   │   ├── base_screen.py        # Base screen class
│   │   ├── dashboard_view.py
│   │   ├── users_view.py
│   │   ├── patrons_view.py
│   │   ├── books_view.py
│   │   ├── borrowed_books_view.py
│   │   ├── payments_view.py
│   │   ├── composite_data_view.py
│   │   ├── data_view.py
│   │   └── attendance_view.py
│   │
│   ├── widgets/                  # Reusable UI widgets
│   │   ├── __init__.py
│   │   ├── base/                 # Base widget classes
│   │   │   ├── __init__.py
│   │   │   ├── material_widget.py
│   │   │   └── responsive_widget.py
│   │   │
│   │   ├── buttons/              # Button components
│   │   │   ├── __init__.py
│   │   │   ├── material_button.py
│   │   │   ├── icon_button.py
│   │   │   └── action_button.py
│   │   │
│   │   ├── cards/                # Card components
│   │   │   ├── __init__.py
│   │   │   ├── material_card.py
│   │   │   ├── stat_card.py
│   │   │   └── info_card.py
│   │   │
│   │   ├── forms/                # Form components
│   │   │   ├── __init__.py
│   │   │   ├── base_form.py
│   │   │   ├── create_user_form.py
│   │   │   ├── create_patron_form.py
│   │   │   ├── create_book_form.py
│   │   │   ├── create_borrowed_book.py
│   │   │   ├── create_payment_form.py
│   │   │   └── validators/
│   │   │       ├── __init__.py
│   │   │       ├── form_validator.py
│   │   │       └── field_validators.py
│   │   │
│   │   ├── tables/               # Table components
│   │   │   ├── __init__.py
│   │   │   ├── data_table.py
│   │   │   ├── sortable_table.py
│   │   │   └── filterable_table.py
│   │   │
│   │   ├── dialogs/              # Dialog components
│   │   │   ├── __init__.py
│   │   │   ├── confirmation_dialog.py
│   │   │   ├── error_dialog.py
│   │   │   └── progress_dialog.py
│   │   │
│   │   ├── navigation/           # Navigation components
│   │   │   ├── __init__.py
│   │   │   ├── sidebar.py
│   │   │   ├── breadcrumb.py
│   │   │   └── tab_bar.py
│   │   │
│   │   └── section/              # Section components
│   │       ├── __init__.py
│   │       ├── material_section.py
│   │       └── collapsible_section.py
│   │
│   └── styles/                   # Styling and themes
│       ├── __init__.py
│       ├── themes/
│       │   ├── __init__.py
│       │   ├── light_theme.py
│       │   ├── dark_theme.py
│       │   └── custom_theme.py
│       │
│       ├── constants.py          # UI constants
│       └── material_design.py    # Material design utilities
│
├── utils/                        # Utility modules
│   ├── __init__.py
│   ├── constants.py              # Application constants
│   ├── helpers.py                # Helper functions
│   ├── decorators.py             # Utility decorators
│   ├── validators.py             # Validation utilities
│   ├── formatters.py             # Data formatters
│   ├── error_handler.py          # Error handling utilities
│   ├── date_utils.py             # Date/time utilities
│   ├── file_utils.py             # File operations
│   └── string_utils.py           # String operations
│
├── config/                       # Configuration management
│   ├── __init__.py
│   ├── app_settings.py           # Application settings
│   ├── database_config.py        # Database configuration
│   ├── logging_config.py         # Logging configuration
│   ├── ui_config.py              # UI configuration
│   └── environments/             # Environment-specific configs
│       ├── __init__.py
│       ├── development.py
│       ├── testing.py
│       └── production.py
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── fixtures/                 # Test fixtures
│   │   ├── __init__.py
│   │   ├── database_fixtures.py
│   │   └── ui_fixtures.py
│   │
│   ├── unit/                     # Unit tests
│   │   ├── __init__.py
│   │   ├── test_controllers/
│   │   ├── test_services/
│   │   ├── test_managers/
│   │   └── test_utils/
│   │
│   ├── integration/              # Integration tests
│   │   ├── __init__.py
│   │   ├── test_database/
│   │   └── test_ui/
│   │
│   └── e2e/                      # End-to-end tests
│       ├── __init__.py
│       └── test_workflows/
│
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── architecture/             # Architecture docs
│   ├── user_guide/               # User guides
│   └── development/              # Development docs
│
├── scripts/                      # Utility scripts
│   ├── __init__.py
│   ├── setup_database.py         # Database setup
│   ├── migrate_data.py           # Data migration
│   ├── generate_reports.py       # Report generation
│   └── backup_data.py            # Data backup
│
├── resources/                    # Static resources
│   ├── icons/                    # Application icons
│   ├── images/                   # Images and graphics
│   ├── fonts/                    # Custom fonts
│   └── templates/                # Document templates
│
├── data/                         # Data files (not in version control)
│   ├── exports/                  # Exported data
│   ├── imports/                  # Import staging
│   ├── backups/                  # Database backups
│   └── logs/                     # Application logs
│
└── deployment/                   # Deployment configurations
    ├── docker/                   # Docker configurations
    │   ├── Dockerfile
    │   └── docker-compose.yml
    ├── scripts/                  # Deployment scripts
    └── configs/                  # Server configurations
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
