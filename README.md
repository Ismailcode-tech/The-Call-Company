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
```


For using ai assistant 
you need api key from groq and Chromadb credentials and langchain to see live ai assistant process
GROQ_API_KEY=YOUR_API_KEY
CHROMA_API_KEY=YOUR_API_KEY
CHROMA_TENANT=YOUR_Chroma_TENANT
CHROMA_DATABASE=YOUR_CHROMA_DATABASE
LANGCHAIN_API_KEY = YOUR_API_KEY
all this modification should be preformed in the .env

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

* Ismail Hadjlarbi – Frontend and Recommandation Engin and Filter Development
* Celia Authentication and Database Development.
* Nabaa Payment and membership systems Development.
* Ranya AI Assistant and membership Development.

---

# License

This project was developed for educational purposes as part of a university software engineering project.



