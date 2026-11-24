# InvenTrack: Inventory Management System

## 1. Project Overview
A Django-based inventory management application providing full product lifecycle management (Create, Read, Update, Delete) augmented with enterprise features: unified search/filtering/sorting, pagination, strict SKU validation, an audit trail, role-based authentication, and a read-only Groq-powered AI assistant.

---

## 2. Tech Stack & Dependencies
- **Framework:** Django 6.1.2 (Python 3.14)
- **Database:** SQLite3 (`InvProject/db.sqlite3`)
- **Frontend / Styling:** Bootstrap 5, Django Crispy Forms
- **AI Integration:** Groq API (`openai/gpt-oss-120b` or `openai/gpt-oss-20b`), implemented via Python standard library (`urllib.request`) — zero extra dependencies.
- **Environment Handling:** Built-in auto-loader for `.env` files in `settings.py`.

---

## 3. Core Features Implemented

### Feature 1: Search, Filter & Sort
- **Search:** Query by product name or SKU (`icontains`).
- **Dropdown Filters:** Filter by specific Supplier or Stock Status (`In Stock (>0)` vs `Out of Stock (0)`).
- **Sorting:** Sort ascending or descending by `Price` or `Quantity`.
- **Unified Querying:** All search, filter, and sort options combine dynamically into a single GET request.

### Feature 2: Pagination
- Product list is paginated at **5 items per page** using Django's built-in `Paginator`.
- Query parameters (search, supplier, stock, sort) are automatically preserved across page transitions.

### Feature 3: Built-in Authentication & Route Protection
- Uses Django's built-in `auth` system (`LoginView`, `logout_view`).
- All product routes (`/list/`, `/create/`, `/update/`, `/delete/`), history (`/history/`), and chatbot (`/chatbot/`) are protected by `@login_required`.
- User accounts are provisioned exclusively via the Django Admin panel (`/admin/`).
- Dynamic navigation bar reflects authentication status and active username.

### Feature 4: Strictly Validated Unique SKU Field
- Enforces fixed SKU format: **`ABC-1234`** (3 uppercase letters, hyphen, 4 digits).
- Regex `^[A-Z]{3}-\d{4}$` enforced both in the model (`validators=[sku_validator]`) and form (`clean_sku()`).
- Automated data migration (`0002_alter_product_sku.py`) safely migrated legacy database rows (e.g., `S3456` &rarr; `SKU-3456`) without data loss.

### Feature 5: Audit Trail
- Model `AuditLog` captures every `CREATE`, `UPDATE`, and `DELETE` event.
- Tracks: **Who** (`username`), **What** (action), **When** (`timestamp`), **Changes** (field-by-field `old -> new` diffs), and a full **Product Snapshot**.
- Deleted items retain their snapshot so historical records remain fully visible.
- Dedicated, read-only UI at `/history/` with pagination and status badges.

### Feature 6: Groq AI Inventory Chatbot
- Read-only conversational assistant querying real-time inventory data.
- Prompt-grounded: answers strictly from current stock records and refuses unrelated inquiries with *"I can only answer questions about your inventory."*
- Session-based conversation memory (last ~10 messages) with a "Clear History" option.
- Handles missing API keys, network outages, and DNS errors gracefully with UI alerts.

---

## 4. Key Project Files

```
Project1/
├── .env                         # Local secrets (GROQ_API_KEY, GROQ_MODEL) [Git-ignored]
├── .env.example                 # Template for environment configuration
├── PROJECT_CONTEXT.md           # This document
└── InvProject/
    ├── manage.py
    ├── db.sqlite3               # SQLite database (existing data preserved)
    ├── InvProject/
    │   ├── settings.py          # App config, auth URLs, .env auto-loader
    │   └── urls.py              # Root URL routing
    └── invapp/
        ├── models.py            # Product and AuditLog models
        ├── forms.py             # productForm with clean_sku validation
        ├── views.py             # CRUD, search/filter/sort, audit logging, chatbot view
        ├── urls.py              # App routes (/list/, /history/, /chatbot/, etc.)
        ├── admin.py             # Model admin registrations
        ├── tests.py             # 8 unit tests covering all features
        ├── migrations/          # Schema and data migrations (0001, 0002, 0003)
        └── templates/invapp/
            ├── layout.html      # Base layout & responsive navigation bar
            ├── login.html       # Sign-in page
            ├── product_list.html# Search, filter, table, pagination
            ├── product_form.html# Create and edit form
            ├── product_confirm_del.html # Deletion confirmation
            ├── history.html     # Read-only audit log viewer
            └── chatbot.html     # AI chatbot chat interface
```

---

## 5. Configuration & Environment Variables

Stored in `.env` at the project root:
| Variable | Description | Default |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | Your Groq API key (`gsk_...`) | *(Required for Chatbot)* |
| `GROQ_MODEL` | LLM model identifier | `openai/gpt-oss-120b` |

---

## 6. Default Admin Credentials

- **URL:** `http://127.0.0.1:8000/login/` (or `/admin/`)
- **Username:** `admin`
- **Password:** `admin123`

---

## 7. Useful Commands

- **Run Dev Server:**
  ```powershell
  python InvProject\manage.py runserver
  ```
- **Run Automated Test Suite:**
  ```powershell
  python InvProject\manage.py test invapp
  ```
- **Create Additional Users (CLI):**
  ```powershell
  python InvProject\manage.py createsuperuser
  ```
