# GuardianGate - Backend

School safety platform. FastAPI + (PostgreSQL coming next).

> The product name is **not** hard-coded. It lives once in `.env` as `APP_NAME`.
> Change that single value and the whole backend rebrands.

## Setup (Windows / PowerShell)

From the project folder in VS Code's terminal:

```powershell
# 1. Create a virtual environment with Python 3.13
py -3.13 -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload
```

Then open:
- http://127.0.0.1:8000/        -> brand-driven JSON response
- http://127.0.0.1:8000/docs    -> interactive API docs (titled from APP_NAME)

## Where the brand name lives

- `.env` -> `APP_NAME=GuardianGate`   (the ONE place you ever change it)
- `app/core/config.py` reads it into `settings.APP_NAME`
- everything else reads `settings.APP_NAME` - never the raw string

## Note for Windows

Don't create `.env` with PowerShell `echo` (it writes UTF-16 and breaks parsing).
Create/edit `.env` inside VS Code instead.

## Structure

```
guardiangate-backend/
  app/
    main.py            FastAPI app (reads brand from settings)
    core/
      config.py        Settings - single source of truth for branding
  .env                 your local config (git-ignored)
  .env.example         template to copy
  requirements.txt
```
