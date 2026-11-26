# LUMINA 2.0 — AI-Driven Cyber Threat Intelligence & Scam Protection

LUMINA is an educational cybersecurity prototype with a premium dark dashboard, separate User and Admin sign-in roles, account registration, ML-assisted message classification, structural URL inspection, explainable risk indicators, scan history, analytics and CSV report export.

## What's upgraded
- **Dual-role authentication:** User login, Admin login, user self-registration, password hashing and server-side session cookies.
- **Role-aware workspace:** Users see their own scans; administrators see the system-wide scan history and aggregate metrics.
- **Advanced frontend:** Responsive dark cybersecurity dashboard, scanner, risk results, recent activity, history and report export.
- **Existing detection retained:** TF-IDF/Logistic Regression text model, text signals, URL heuristics and explainable risk engine.
- **Persistent analytics:** SQLite-backed scan metrics and history.

## Demo credentials
**Administrator**
- Email: `admin@lumina.local`
- Password: `Admin@123`

Users can create their own account from the User login screen. Admin access is not available through public registration.

**Important:** The administrator credentials are for local demonstration only. Change the password before any deployment. Set a unique `LUMINA_SECRET` environment variable before running outside a local demo. This prototype is not production-hardened and should not be exposed directly to the public internet.

## Run on Windows
1. Extract the ZIP and open the `LUMINA` folder in VS Code.
2. Open a terminal and run:
   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   python train_model.py
   python app.py
   ```
3. Keep the backend terminal running. It serves `http://127.0.0.1:5000`.
4. Open a second terminal in the project root and run:
   ```powershell
   py -m http.server 8080 --directory frontend
   ```
5. Open `http://127.0.0.1:8080` in Chrome.
6. Choose **Admin login** and use the demo credentials, or choose **User login** and create a user account.

You can also use `START_LUMINA.bat` after installing dependencies in `backend/.venv` to start the API.

## API endpoints
- `GET /api/health` — backend health check
- `POST /api/register` — create a user account
- `POST /api/login` — authenticate as user or admin (`role` must match account role)
- `GET /api/me` — current session user
- `POST /api/logout` — end session
- `POST /api/analyze` — analyze text or URL (login required)
- `GET /api/stats` — role-scoped metrics
- `GET /api/history` — user scans or all scans for admin
- `DELETE /api/history` — clear current user's scans; admin clears all scans

## Security and detection limitations
- The included CSV is a small starter dataset and is not representative of all scams. Model performance must be measured on a larger, independent test set.
- The risk score is a heuristic/model-based **risk indicator**, not a calibrated probability of fraud.
- URL analysis is offline and structural. LUMINA does not visit submitted URLs, inspect page content, or query a live threat-intelligence provider in this build.
- HTTPS does not prove that a website is legitimate. A SAFE result is not a guarantee.
- The Chrome extension source is retained as a prototype. The new authenticated API requires a compatible extension sign-in/session flow before extension scans will work; use the authenticated web dashboard for the complete 2.0 workflow.
- This project is an educational prototype, not a replacement for security products or professional incident response.

## Project structure
```text
LUMINA/
  backend/       Flask API, authentication, ML training, analyzers, SQLite
  frontend/      Responsive dashboard and login experience
  extension/     Chrome Manifest V3 prototype (session integration pending)
  tests/         Analyzer tests
```
