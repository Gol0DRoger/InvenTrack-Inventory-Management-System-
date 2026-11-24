
# InvenTrack — Inventory Management System

A Django-based inventory management application providing full product lifecycle management (Create, Read, Update, Delete) augmented with enterprise features: unified search/filtering/sorting, pagination, strict SKU validation, an audit trail, role-based authentication, and a read-only Groq-powered AI assistant.

---

## 📸 Demo & Screenshots

### Application Walkthrough
<!-- Add your demo video or GIF link below -->

https://github.com/user-attachments/assets/7074cb3b-f6a5-4b10-b667-c9173379061f


### Screenshots

<img width="959" height="502" alt="Screenshot 2026-11-24 205824" src="https://github.com/user-attachments/assets/1e6c74f5-d3c2-465a-af71-11f6b41dd5c8" />
<img width="959" height="500" alt="Screenshot 2026-11-24 205944" src="https://github.com/user-attachments/assets/e3b47d67-e2ec-48b1-a88d-aa2291a8ff2d" />
<img width="959" height="539" alt="Screenshot 2026-11-24 210042" src="https://github.com/user-attachments/assets/f5f32f22-c0a5-4199-8205-3d577c77e954" />


---

## ✨ Key Features

- **Product CRUD & Real-Time Filtering:** Manage items with instant multi-parameter search (Name/SKU), supplier dropdowns, stock level filters (`In Stock` / `Out of Stock`), and price/quantity sorting.
- **Smart Pagination:** Built-in 5-item pagination that preserves active filter and search states across page turns.
- **Strict SKU Validation:** Enforces standard enterprise SKU formats (`ABC-1234`) with regex validation in both the database model and form inputs.
- **Immutable Audit Trail:** Automatically records all `CREATE`, `UPDATE` (field-level diffs: `old -> new`), and `DELETE` actions. Product snapshots are preserved so deleted items remain visible in historical logs.
- **AI Inventory Chatbot:** Read-only assistant powered by Groq LLMs (`openai/gpt-oss-120b`). Strictly answers based on current inventory data, politely rejects off-topic queries, and stores recent session history.
- **Role-Based Access Control:** Built-in Django authentication. All inventory endpoints and chatbot views require login; user creation is restricted to administrators.

---

## 🛠️ Tech Stack

- **Backend:** Python & Django
- **Database:** SQLite3
- **Frontend:** Bootstrap 5 & Django Crispy Forms
- **AI Integration:** Groq API (via standard library `urllib` — zero extra dependencies)
- **Configuration:** Auto-loads `.env` locally without third-party packages

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment
```powershell
git clone <YOUR-GITHUB-REPO-URL>
cd Project1
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
# (or install Django and crispy forms: pip install django django-crispy-forms crispy-bootstrap5)
```

### 3. Environment Setup
Create a `.env` file in the project root (refer to `.env.example`):
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

### 4. Database Setup & Run
```powershell
python InvProject\manage.py migrate
python InvProject\manage.py runserver
```
Visit the app in your browser at: **`http://127.0.0.1:8000/`**

---

## 🔐 Default Admin Credentials

For local testing and review:
- **URL:** `http://127.0.0.1:8000/login/` (or `/admin/`)
- **Username:** `admin`
- **Password:** `admin123`

---

## 🧪 Running Automated Tests

Run the full test suite covering search, pagination, validation, audit logs, auth, and chatbot handling:
```powershell
python InvProject\manage.py test invapp
```

---

## 📂 Project Structure

```text
Project1/
├── .env.example                 # Configuration template
├── README.md                    # Project documentation
└── InvProject/
    ├── manage.py                # Django CLI
    ├── InvProject/              # Core project settings and URL routing
    └── invapp/
        ├── models.py            # Product and AuditLog models
        ├── forms.py             # Form validation & SKU normalization
        ├── views.py             # Business logic, audit tracking, Groq client
        ├── urls.py              # Application routes
        ├── tests.py             # Automated unit tests
        └── templates/invapp/    # Bootstrap responsive views
```
