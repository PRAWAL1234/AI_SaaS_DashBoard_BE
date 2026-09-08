# ⚙️ AI Resume Analyzer - Backend API

This is the production-ready asynchronous backend service for the AI Resume SaaS Platform. Built using Python and FastAPI, this API handles secure JWT authentication, document parsing communication, and structured database operations with PostgreSQL.

---

## 🛠️ Tech Stack & Infrastructure

- **Framework:** Python / FastAPI
- **Database ORM:** SQLModel (SQLAlchemy + Pydantic)
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens) with Passlib & Jose
- **Migration Tool:** Alembic

---

## 🚀 Local Installation

1. Create and activate virtual environment:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations and start server:
   ```bash
   alembic upgrade head
   uvicorn main:app --reload
   ```
