# The Call – Mobile Network Recommendation Platform

## Overview

**The Call** is a full-stack web application designed to help users find the most suitable mobile phone plan based on their preferences and budget.

Users can compare plans from multiple mobile providers, receive personalized recommendations, manage their membership, and securely access their account through two-factor authentication.

The project was developed using **React + TypeScript** for the frontend and **Flask + MySQL** for the backend.

---

# Features

### User Authentication

* User registration
* Secure login
* Email verification using One-Time Password (OTP)
* JWT authentication
* Secure HttpOnly Cookie session management
* Automatic access token refresh
* Logout functionality

### Recommendation Engine

* Personalized mobile plan recommendations
* Budget-aware filtering
* Data allowance matching
* Calls and texts matching
* Phone brand filtering
* Priority-based ranking (Price, Data or Calls)
* Returns the three best matching plans

### Membership Management

* View active membership
* Membership dashboard
* Current plan information
* Renewal date
* Membership ID

### Plan Browser

* Browse all available plans
* Filter by provider
* Filter by plan type
* Filter by budget
* Filter by phone brand
* Filter by data allowance
* Filter by calls and texts

### Responsive Design

* Desktop support
* Tablet support
* Mobile support

---

# Technologies Used

## Frontend

* React
* TypeScript
* React Router
* Tailwind CSS
* Lucide React Icons
* Vite

## Backend

* Python
* Flask
* SQLAlchemy
* JWT Authentication
* Cerberus Validation
* Flask-Mail

## Database

* MySQL

---

# Project Structure

```text
TheCall/
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── lib/
│   │   ├── assets/
│   │   └── App.tsx
│   │
│   └── package.json
│
├── backend/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── utils/
│   ├── config.py
│   └── app.py
│
└── README.md
```

---

# System Architecture

```text
                User
                  │
                  ▼
      React + TypeScript Frontend
                  │
          API Layer (_base.ts)
                  │
                  ▼
             Flask REST API
                  │
         Recommendation Engine
                  │
                  ▼
             MySQL Database
```

---

# Recommendation Engine

The recommendation engine recommends the best mobile plans according to the user's requirements.

The recommendation process consists of four steps:

1. Filter plans

   * Plan type
   * Phone brand
   * Budget

2. Calculate scores

   * Data score
   * Price score
   * Calls & texts score

3. Apply user priority

   * Price
   * Data
   * Calls

4. Rank plans and return the Top 3 recommendations.

If no exact matches are found, the system returns the closest alternatives.

---

# Authentication Flow

```text
Register
      │
      ▼
Receive OTP by Email
      │
      ▼
Verify OTP
      │
      ▼
Backend issues JWT Tokens
      │
      ▼
HttpOnly Cookies
      │
      ▼
Authenticated Session
```

---

# Security

The application includes several security mechanisms:

* Password hashing
* JWT Authentication
* HttpOnly Cookies
* Refresh Token Rotation
* Two-Factor Authentication (OTP)
* Server-side validation
* Protected API endpoints

---

# Installation

## Clone the Repository

```bash
git clone

```

---

## Backend Setup

Create a virtual environment

```bash
python -m venv venv
```
Install dependencies

```bash
pip install -r requirements.txt
```


Configure your MySQL database.

The database connection is configured for the developer's local
MySQL setup. Before running the app, update the connection
string in .env to match your own MySQL credentials:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost/the_call_db'
    


The databases must be created in MySQL Workbench first:

    CREATE DATABASE the_call_db;

Update the database configuration.

Start Flask
```bash
python -m flask --app website run --debug
```


The backend runs on

```bash
http://localhost:5000
```

---
## Backend Setup — Important Notes

### Environment variables (.env)

Create a `.env` file in the project root (next to `app.py`) with the following:

    SECRET_KEY=any_random_string_here
    SQLALCHEMY_DATABASE_URI=mysql+pymysql://YOUR_USERNAME:YOUR_PASSWORD@localhost/the_call_db

    MAIL_USERNAME=thecallsupport@gmail.com
    MAIL_PASSWORD=ejyu ibwb evct iiix
    MAIL_DEFAULT_SENDER=thecallsupport@gmail.com

    GROQ_API_KEY=YOUR_API
    LANGCHAIN_API_KEY=YOUR_API
    CHROMA_API_KEY=YOUR_API
    CHROMA_TENANT=YOUR_TENANT
    CHROMA_DATABASE=YOUR_DATABASE

**Important:** `LANGCHAIN_API_KEY` must have *some* value, even a placeholder like `dummy`,
or the app will crash on startup with `TypeError: str expected, not NoneType` — even if
you don't plan to use the AI assistant feature.


### Activating the virtual environment

After `python -m venv venv`, you must activate it before installing anything:

- Windows (cmd): `venv\Scripts\activate`
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- macOS/Linux: `source venv/bin/activate`

You'll see `(venv)` at the start of your terminal prompt when it's active.

### Windows: keep the project path short

Some dependencies (`torch`, pulled in by `sentence-transformers`) create very deeply
nested folders on install. If your project sits in a long path (e.g. inside `Downloads`
with spaces/parentheses in folder names), installation can fail with:

    OSError: [WinError 206] The filename or extension is too long

Fix1: place the project somewhere shallow, e.g. `C:\dev\thecall`, or enable long path
support in Windows (`regedit` → `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
→ set `LongPathsEnabled` to `1` → restart).

Fix2: Change the outer and inner folders names to shorter names to resolve the issue.

### Seeding the database with sample plans

After running Flask once (so the tables are created), seed the plan/provider data:

```bash
python -m website.database_data
```

Without this step, `/api/plans` will work but return an empty list.

### If you change a database model later

`db.create_all()` only creates tables that don't exist yet — it never updates existing
ones. If you edit a model and get an error like `Unknown column 'x' in 'field list'`,
drop that specific table in MySQL Workbench and restart Flask so it's recreated with the
new schema:

    DROP TABLE table_name;

### AI Assistant first run

The first time you use the AI assistant after installing `sentence-transformers`, it will
download an embedding model from Hugging Face (a few hundred MB). This is normal and only
happens once — expect a slow startup the first time, then it's cached and fast after that.

### Dependency versions

This project pins the entire `langchain` family (`langchain`, `langchain-core`,
`langchain-groq`, `langchain-chroma`, `langchain-huggingface`, `langgraph`) to
compatible versions in `requirements.txt`. These packages update frequently and
break compatibility with each other across major versions, so **do not upgrade
any single langchain-related package individually** — if you need to update one,
update them all together and re-verify with:

    pip check

Last note: Don't before creating a virtual environment and installing the dependencies to move 
to the project folder by using the the 'cd' command.


---
## Frontend Setup

Install dependencies

```bash
npm install
```

Run the development server
enter to the frontend folder
```bash
cd frontend
```
```bash
npm run dev
```

The frontend runs on

```
http://localhost:5173



---

# API Overview

Authentication

```
POST /api/auth/signup
POST /api/auth/signin
POST /api/auth/verify-2fa
POST /api/auth/resend-otp
POST /api/auth/refresh
POST /api/auth/logout
```

Plans

```
GET /api/plans
GET /api/plans/{id}
GET /api/plans/recommend
```

Membership

```
GET /api/membership
POST /api/membership
PUT /api/membership
```

---

# Frontend Highlights

* Component-based architecture
* Type-safe development with TypeScript
* Centralized API layer
* Reusable UI components
* Responsive layouts
* Protected routes
* Automatic token refresh

---

# Backend Highlights

* RESTful API
* Service-layer architecture
* SQLAlchemy ORM
* Recommendation Engine
* JWT authentication
* Email verification
* Secure session management

---

# Future Improvements

* User preference history
* Plan comparison charts
* Payment integration
* Admin dashboard
* Push notifications
* Mobile application

---

# Contributors

* Ismail Hadjlarbi – Frontend and Recommandation Engine and Filter Development
* Celia Authentication and Database Development.
* Nabaa Payment and membership systems Development.
* Ranya AI Assistant and membership Development.

---

# License

This project was developed for educational purposes as part of a university software engineering project.



