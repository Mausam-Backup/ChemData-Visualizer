# 🚀 Deployment Guide

This guide details how to deploy the **ChemData Visualizer** full-stack application for free using **Render** (Backend) and **Vercel** (Frontend).

---

## ⚠️ Critical Warnings & Limitations

### 1. 🛑 SQLite & Ephemeral Storage (The "Free Database" Trap)

By default, this project uses **SQLite** (`db.sqlite3`).

> **IMPORTANT**: On cloud platforms like Render, Heroku, or AWS App Runner, the file system is **ephemeral**. This means every time your app restarts or deploys:
>
> - **YOUR DATABASE FILE IS DELETED/RESET.**
> - **ALL UPLOADED MEDIA FILES (CSVs) ARE DELETED.**

**Why?** These platforms destroy the container and create a new one for every update.
**Solution**: To have persistent data, you **MUST** use an external database like **PostgreSQL** (available on Render, Supabase, or Neon) and an external storage service like **AWS S3** or **Cloudinary** for media files.

### 2. ⏳ Render Free Tier "Spin Down"

Render's free tier spins down your web service after **15 minutes of inactivity**.

- The next request will take **30-50 seconds** to load while the server boots up.
- **Fix**: Use a free uptime monitor (details below) to keep it awake.

---

## 🛠️ Part 1: Backend Deployment (Render)

### Prerequisites

1.  Ensure you have a `requirements.txt` in your `backend/` folder (already present).
2.  Ensure you have a `build.sh` or similar (optional, but standard build commands work too).
3.  **Push your code to GitHub.**

### Steps

1.  **Create Account**: Log in to [dashboard.render.com](https://dashboard.render.com/).
2.  **New Web Service**: Click **New +** -> **Web Service**.
3.  **Connect Repo**: Select your `ChemData-Visualizer` repository.
4.  **Configuration**:
    - **Name**: `chemviz-backend` (or similar)
    - **Region**: Closest to you (e.g., Singapore, Frankfurt).
    - **Branch**: `main`
    - **Root Directory**: `backend` (Important! This tells Render where `manage.py` is).
    - **Runtime**: **Python 3**
    - **Build Command**: `pip install -r requirements.txt && python manage.py migrate`
    - **Start Command**: `gunicorn core.wsgi:application`
5.  **Environment Variables**:
    Add the following in the "Environment" tab:
    - `PYTHON_VERSION`: `3.10.12` (or your local version)
    - `SECRET_KEY`: (Generate a strong random string)
    - `DEBUG`: `False`
    - `ALLOWED_HOSTS`: `*` (or your render URL `chemviz-backend.onrender.com`)
6.  **Deploy**: Click "Create Web Service".

### 💡 Pro Tip: Keeping it Alive

To prevent the 50-second delay on wake-up:

1.  Sign up for [UptimeRobot](https://uptimerobot.com/) (Free).
2.  Create a strict "HTTP(s)" monitor.
3.  URL: `https://your-app-name.onrender.com/api/datasets/` (or any valid endpoint).
4.  Interval: **Every 10 minutes**.
    - _Note: This consumes your Render free monthly computation hours faster, but keeps the app responsive._

---

## 🌐 Part 2: Frontend Deployment (Vercel)

### Prerequisites

1.  Backend is deployed and you have the URL (e.g., `https://chemviz-backend.onrender.com`).

### Steps

1.  **Create Account**: Log in to [vercel.com](https://vercel.com/).
2.  **Import Project**: Click **Add New...** -> **Project**.
3.  **Select Repo**: Import `ChemData-Visualizer`.
4.  **Framework Preset**: Select **Vite**.
5.  **Root Directory**:
    - Click "Edit" next to Root Directory.
    - Select `web-frontend`.
6.  **Build Configuration** (Auto-detected usually):
    - Build Command: `npm run build`
    - Output Directory: `dist`
7.  **Environment Variables**:
    Expand the "Environment Variables" section and add:
    - `VITE_API_URL`: `https://your-backend-app.onrender.com`
      _(Note: Do **not** add a trailing slash `/` at the end)_
    - `VITE_GOOGLE_CLIENT_ID`: (Your Google OAuth ID if using login)
8.  **Deploy**: Click "Deploy".

---

## 🔗 Part 3: connecting Them

1.  **CORS Configuration (Backend)**:
    - Once Vercel provides your frontend domain (e.g., `https://chemviz.vercel.app`), go back to your **Django settings**.
    - Update `CORS_ALLOWED_ORIGINS` or `CORS_ALLOW_ALL_ORIGINS = True` (for testing) to allow requests from the Vercel domain.
    - Commit and push changes. Render will auto-redeploy.

2.  **Verify**:
    - Open your Vercel URL.
    - Try logging in or fetching data.
    - If it fails, check the Console (F12) for CORS errors or 404s.

---

## 📝 Summary of Trade-offs

| Feature         | Local Development   | Free Cloud Deployment (e.g., Render/Vercel) |
| :-------------- | :------------------ | :------------------------------------------ |
| **Cost**        | Free                | Free                                        |
| **Database**    | Persistent (SQLite) | **Ephemeral (Resets on restart)** ⚠️        |
| **Speed**       | Instant             | Slow initial load (Spin down)               |
| **Media Files** | Stored locally      | Deleted on restart ⚠️                       |
| **Setup**       | Simple              | Moderate (Requires Env Vars & Config)       |

**Recommendation for "Real" Production**:
If you need this project to hold data permanently, you must spin up a managed PostgreSQL instance (Render has a paid tier, or use a free tier from **Supabase** or **Neon**) and connect Django to it.
