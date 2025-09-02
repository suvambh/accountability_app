# ⚡ Accountability Launcher — FastAPI MVP

A focused, installable web app that helps you **choose a learning activity**, **launch the right resource** (video/book/notebook/Kaggle/VS Code), **track a timed session**, and **log results** with **XP, streaks, and analytics**. Notes can be uploaded as Markdown and viewed later.

* Backend: **FastAPI** + **SQLAlchemy** (SQLite in dev)
* Frontend: **Jinja2** templates + **Chart.js** (via CDN)
* Styling: single shared CSS (dark “terminal” theme)
* Data: CSV seeding utilities
* Analytics: total time, time by resource type, session length distribution, XP growth

---

## ✨ Features

* **Resource dictionary** (videos, books, notebooks, Kaggle links, code/projects)
* **Start Session**: pick from DB or add a custom resource; set goal & time
* **Active Session**: timer + **auto-open resource link** in a new tab
* **Finish Session**: completion %, outcome, and **upload Markdown notes**
* **XP + Streaks**: XP per session, levels (1000 XP per level), day streaks
* **Dashboard**: quick overview + shortcuts
* **Logs**: full table view of your sessions (+ link to uploaded notes)
* **Analytics** (Chart.js):

  * Total time
  * Time by resource type
  * Session length distribution (histogram)
  * XP growth over time (line chart)
* **API + UI** for logs/resources (HTML pages & JSON endpoints)
* **Dark terminal CSS** shared across the app

---

## 🗂️ Project Structure

```
accountability-app/
│
├─ app/
│  ├─ main.py
│  ├─ database.py            # SQLAlchemy engine/session
│  ├─ models.py              # ORM models + enums
│  ├─ crud.py                # DB operations
│  ├─ services/
│  │   └─ xp.py              # XP & streak logic (pure functions)
│  ├─ routers/
│  │   ├─ dashboard.py       # /dashboard (HTML)
│  │   ├─ session.py         # /session/... (start/active/finish UI)
│  │   ├─ logs.py            # /logs (HTML) + /logs/api (JSON)
│  │   └─ resources.py       # /resources (HTML) + /resources/api (JSON)
│  ├─ templates/
│  │   ├─ dashboard.html
│  │   ├─ session_start.html
│  │   ├─ session_active.html
│  │   ├─ session_finish.html
│  │   ├─ logs.html
│  │   └─ analytics.html
│  └─ utils/
│      └─ seed_csv.py        # seed users/resources/logs from CSV
│
├─ static/
│  └─ style.css              # dark terminal theme
│
├─ uploads/                  # uploaded markdown notes (gitignored)
├─ data/
│  ├─ users.csv
│  ├─ resources.csv
│  └─ logs.csv
│
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 🚀 Quickstart

**Prereqs**: Python 3.10+ recommended.

```bash
# 1) Clone and enter
git clone https://github.com/suvambh/accountability_app.git
cd accountability-app

# 2) Create venv
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# 3) Install deps
pip install -r requirements.txt

# 4) (Optional) Seed demo data
python app/utils/seed_csv.py

# 5) Run server
uvicorn app.main:app --reload

# 6) Open
# http://localhost:8000/dashboard
```

> The app uses SQLite by default and **creates tables on startup**.

---

## 🛠️ Configuration (Dev)

* **Database**: in `app/database.py`. Defaults to SQLite.
  For Postgres later, set a `DATABASE_URL` and swap the engine.
* **Static & uploads**: in `app/main.py`, mount:

  * `/static` → `static/`
  * `/uploads` → `uploads/`

Make sure `uploads/` exists (the app will `os.makedirs` when saving files).

---

## 🧰 Models / Schema

### Enums

```python
class ResourceType(str, enum.Enum):
    video = "video"
    book = "book"
    notebook = "notebook"
    kaggle = "kaggle"
    code = "code"
    project = "project"
    other = "other"  # optional

class Mode(str, enum.Enum):
    watch = "watch"
    read  = "read"
    code  = "code"

class Status(str, enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class Outcome(str, enum.Enum):
    clear = "clear"
    confused = "confused"
    needs_review = "needs_review"
    breakthrough = "breakthrough"
    other = "other"
```

### Tables (key fields)

**User**

* `id`, `name`
* `xp` (int), `level` (int)
* `current_streak` (int), `longest_streak` (int)
* `last_active_date` (date)

**Resource**

* `id`, `name`, `type` (enum), `link`
* `chapter_number` (int, nullable)
* `duration` (int minutes, optional total resource length)
* `details` (str, optional)

**ActivityLog**

* `id`, `user_id`, `resource_id`
* `chapter_number` (nullable)
* `mode` (watch/read/code)
* `goal` (str), `time_allocated` (min)
* `start_time`, `end_time`, `date`
* `status` (active/completed/cancelled)
* `completion_percent` (float)
* `outcome` (Outcome)
* `notes` (text, optional)
* `notes_file` (str path to uploaded .md)
* `xp_earned` (int)

---

## 🎮 XP & Streak Logic (MVP)

In `app/services/xp.py` (pure functions; called from routers):

**XP calculation (example MVP):**

```python
# base minutes * completion% * multipliers
MODE_MULT = {"watch": 1.0, "read": 1.1, "code": 1.3}
OUTCOME_MULT = {"breakthrough": 1.2, "clear": 1.0, "needs_review": 0.9, "confused": 0.8, "other": 1.0}

def calculate_xp(log):
    minutes = max(0, log.time_allocated or 0)
    comp = max(0.0, min(1.0, (log.completion_percent or 0)/100.0))
    m_mult = MODE_MULT.get(log.mode.value if hasattr(log.mode, "value") else log.mode, 1.0)
    o_mult = OUTCOME_MULT.get(log.outcome.value if hasattr(log.outcome, "value") else log.outcome, 1.0)
    return int(round(minutes * comp * m_mult * o_mult))
```

**Levels & streaks (example MVP):**

* **Level up** every **1000 XP** (carry remainder).
* **Streak** increments if `date == last_active_date + 1 day`, otherwise resets to 1. Track `longest_streak`.

```python
def update_user_progress(user, xp_earned, session_date=None):
    user.xp += xp_earned
    # levels
    while user.xp >= (user.level * 1000):
        user.level += 1
    # streaks
    from datetime import timedelta
    if user.last_active_date and session_date:
        if session_date == user.last_active_date + timedelta(days=1):
            user.current_streak += 1
        elif session_date != user.last_active_date:
            user.current_streak = 1
    else:
        user.current_streak = max(1, user.current_streak or 0)
    user.longest_streak = max(user.longest_streak or 0, user.current_streak or 1)
    user.last_active_date = session_date or user.last_active_date
```

> Tweak multipliers/thresholds to taste—these are simple defaults.

---

## 🧭 UI Pages (HTML)

* **Dashboard**: `/dashboard`
  Overview (user, XP), quick links to start session / logs / resources / analytics.
* **Start Session**: `/session/start` (GET form, POST to create log)

  * Choose resource from DB or enter **custom** (with type and optional link).
  * Set **mode**, **goal**, **time\_allocated**.
* **Active Session**: `/session/active/{log_id}`

  * Shows timer; **auto-opens resource link** in new tab if present.
  * Auto-redirects to finish when time elapses.
* **Finish Session**: `/session/finish/{log_id}` (GET form, POST submit)

  * Set completion %, outcome, **upload `.md` notes**.
* **Logs (UI)**: `/logs`

  * Table of sessions with link to uploaded notes.
* **Resources (UI)**: `/resources`

  * Table of resources with type, chapter, link (if any).
* **Analytics**: `/analytics`

  * Cards (total time, avg session) + charts (pie, bar, line).

> **Note**: `/uploads` is mounted to serve uploaded Markdown files.

---

## 🧪 API Endpoints (JSON)

**Logs**

* `GET /logs/api` — list logs (JSON)
* `POST /logs` — create log (user\_id, resource\_id, mode, goal?, time\_allocated?)
* `POST /logs/{log_id}/complete` — set completion & outcome; computes XP & updates user
* `PUT /logs/{log_id}` — update completion/outcome/notes
* `DELETE /logs/{log_id}` — delete

**Resources**

* `GET /resources/api` — list resources
* `POST /resources/api` — create resource
* `PUT /resources/api/{id}` — update resource
* `DELETE /resources/api/{id}` — delete

> These live alongside the UI routes (HTML) under the same `logs.py` / `resources.py` files.

---

## 🧾 CSV Seeding

Script: `app/utils/seed_csv.py` (uses `data/*.csv`).

### `data/users.csv`

```
name
Alice
```

### `data/resources.csv`

```
name,type,link,chapter_number,duration,details
Lesson 1 - Getting Started,video,https://...,1,82,Part 1
...
Chapter 1 - Intro,book,,,,"Book"
...
```

### `data/logs.csv` (full schema)

```
user_id,resource_id,chapter_number,mode,goal,time_allocated,start_time,end_time,date,status,completion_percent,outcome,notes,xp_earned,notes_file
1,1,1,watch,Understand intro,82,2025-01-01 09:00:00,2025-01-01 10:22:00,2025-01-01,completed,100,clear,,82,
...
```

Run:

```bash
python app/utils/seed_csv.py
```

> Tip: If you hit uniqueness errors (e.g., duplicate users), clear tables in the seeder or use unique names.

---

## 🖼️ Styling (Dark Terminal Theme)

Single shared CSS: `static/style.css`

* Monospace (`Fira Code`)
* Dark background `#0d1117`, cyan headers, terminal-green buttons
* Cards, navbar, tables all themed
* Add this in every template:

  ```html
  <link rel="stylesheet" href="/static/style.css">
  ```

**Show/hide helpers**:

```css
.hidden { display: none; }
```

> If sections don’t toggle, make sure `.hidden` exists.

---

## 🧩 Common Pitfalls & Fixes

* **File upload error**: `Expected UploadFile, got <class 'str'>`

  * Your form **must** use `enctype="multipart/form-data"` and `method="post"`, and the `<input name="notes_file" type="file">` must match the parameter name.

* **405 Method Not Allowed** on finish form

  * You need **both** routes: `GET /session/finish/{id}` (show form) **and** `POST /session/finish/{id}` (handle).

* **IsADirectoryError: uploads/**

  * Happens when `notes_file.filename` is empty. Guard with `if notes_file and notes_file.filename:` before writing.

* **Auto-open blocked** by browser

  * `window.open` can be blocked by popup blockers. Allow popups for `localhost`.

* **Reserved attribute `metadata`** in SQLAlchemy models

  * Don’t name columns `metadata` on declarative models; use `details` instead.

* **UI toggles don’t work after CSS change**

  * Ensure `.hidden { display:none; }` exists in CSS.

---

## 🧭 Roadmap

* **V2**: Semantic search (vector DB) to find best resource for a goal; richer gamification (badges, quests)
* **V3**: App tracking (verify external apps/links actually opened); focus metrics
* **V4**: Turn into a **fast.ai training companion** (deep integration with notebooks, projects, structured curricula)

---

## 📦 Requirements

`requirements.txt` should include (example):

```
fastapi
uvicorn
sqlalchemy
jinja2
python-multipart
pydantic
```

(Optionally add `alembic` when you start migrations, and `psycopg[binary]` if moving to Postgres.)

---

## 🧪 Running Tests (optional suggestion)

* Add `pytest`, and start with pure function tests for `app/services/xp.py`.
* Seed small in-memory SQLite DB for API route tests.

---

## 🤝 Contributing

* Use feature branches; open PRs with clear scope.
* Keep **UI routes** (HTML) and **API routes** (JSON) both working.
* Prefer **pure functions** in `services/` for logic (easy to test and reuse).

---

## 📄 License

Choose a license (MIT is common for apps like this). Add a `LICENSE` file in the repo root.

---

## 🙏 Acknowledgments

* Thanks to the **fast.ai** community for inspiration.
* Built with **FastAPI**, **SQLAlchemy**, **Jinja2**, and **Chart.js**.


Happy FastAI—and keep the streak alive! ⏱️📈
