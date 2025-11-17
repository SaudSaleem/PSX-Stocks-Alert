# 📈 Stocks-Alert

A full-stack application that tracks Pakistan Stock Exchange (PSX) stocks in real-time, lets users create price alerts (take-profit, stop-loss, trailing stop, dip-buy & more) and emails them when a trigger fires.

* **Backend:** FastAPI • SQLAlchemy • PostgreSQL • Selenium • APScheduler • JWT Auth
* **Frontend:** Vue 3 • Vite • TailwindCSS (found in `frontend/` – optional)

> Live API documentation is automatically available when the server is running at **`http://localhost:8000/docs`** (Swagger UI).

---

## 🚀 Features

1. User registration, login & JWT-based authentication.
2. Scrapes PSX prices every few minutes **only during trading hours** (09:20 ‑ 16:40 PKT) using Selenium (headless Chrome).
3. Background scheduler evaluates every user alert and sends HTML emails when conditions are met.
4. Supports multiple alert types:
   - Take-profit (tp1, tp2, tp3)
   - Stop-loss (absolute & percentage)
   - Trailing stop (percentage)
   - Box-break & Dip-buy levels
5. RESTful API for managing alerts (`create / update / delete / list`).
6. Vue 3 dashboard (optional) that consumes the API.

---

## 🗂️ Project Structure (important bits)

```txt
stocks-alert/
├── app/              # Python backend source
│   ├── main.py       # FastAPI entry-point
│   ├── models.py     # SQLAlchemy models
│   ├── schemas.py    # Pydantic schemas
│   ├── crud.py       # CRUD helpers
│   ├── tasks.py      # Alert evaluator & email sender
│   ├── psx_scrapper.py # Selenium scraper & scheduler
│   └── data/         # Cached market snapshots
├── alembic/          # (optional) DB migrations
├── frontend/         # Vue 3 client (optional)
├── requirements.txt  # Python deps
└── README.md
```

---

## 🛠️ Prerequisites

| Tool | Version | Purpose |
| ---- | ------- | ------- |
| Python | 3.10+ | backend |
| Node   | 18+   | frontend (optional) |
| Google Chrome | latest | used by headless Selenium |

Make sure `chromedriver` is available. We use [`webdriver-manager`](https://pypi.org/project/webdriver-manager/) so it is downloaded automatically.

---

## 🏗️ Backend – Quick Start

```bash
# 1. Clone repository & enter folder
$ git clone https://github.com/your-user/stocks-alert.git
$ cd stocks-alert

# 2. Create and activate virtual environment (macOS/Linux)
$ python3 -m venv venv
$ source venv/bin/activate

# 3. Install dependencies
(venv) $ pip install -r requirements.txt

# 4. Setup Database (Supabase)
# Get your Supabase connection string from:
# Supabase Dashboard > Settings > Database > Connection String (URI)
# See SUPABASE_MIGRATION.md for detailed setup instructions

# 5. Create .env file with database and email configuration
#    Copy from env.example and update with your values
$ cp env.example .env

# Edit .env with your settings:
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.xxx.supabase.co:5432/postgres
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=app_or_login_password
MAIL_FROM=your_email@example.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_STARTTLS=True

# 6. Run database migrations
(venv) $ alembic upgrade head

# 7. Run the API (reloads on code changes)
(venv) $ uvicorn app.main:app --reload
```

The scraper & alert scheduler start **automatically** with the API. They wake up only during PSX trading hours to save resources.

Manual commands:

```bash
# Run Selenium scraper once
python -m app.psx_scrapper

# Force evaluation of all alerts immediately
python -m app.tasks

# Re-initialise database (⚠️ destructive)
rm ./stocks_alert.db
python -m app.init_db
```

---

## 🎨 Frontend (optional)

```bash
$ cd frontend
$ npm install        # install packages
$ npm run dev        # dev server → http://localhost:5173
```

You can edit `frontend/src` to customise the dashboard or build static files via `npm run build`.

---

## 🔑 Authentication Workflow

1. `POST /register` – create account
2. `POST /login` or `POST /login/json` – receive JWT access token
3. Include header `Authorization: Bearer <token>` for all protected routes (`/alert`, `/alerts`, etc.).

---

## 📬 Email Templates

Emails are sent through the SMTP server you configure in `.env`. Any provider will work as long as it supports STARTTLS.

---

## 🧪 Running the Example Test Suite

```bash
(venv) $ python -m app.test_api
```
The script performs a full register-login-create-alert flow against a local server.

---

## 🤝 Contributing

1. Fork the repo & create your branch: `git checkout -b feat/awesome`.
2. Commit your changes: `git commit -m "feat: add awesome"`.
3. Push to the branch: `git push origin feat/awesome`.
4. Open a Pull Request.

---

## 📜 License

This project is released under the MIT License – see the `LICENSE` file for details.