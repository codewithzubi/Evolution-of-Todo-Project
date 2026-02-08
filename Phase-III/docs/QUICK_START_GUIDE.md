# 🚀 Task Management App - Quick Start Guide

**Status**: ✅ **READY TO RUN**

All dependencies installed. All configurations done. Backend connected to Neon database.

---

## 📋 What's Been Set Up

✅ **Backend Dependencies** - FastAPI, SQLAlchemy, asyncpg installed
✅ **Frontend Dependencies** - Next.js, React, TailwindCSS installed
✅ **Database** - Neon PostgreSQL tables created (users, tasks)
✅ **Environment Variables** - Configured for Neon connection
✅ **Startup Scripts** - Created for easy launching

---

## 🎯 How to Run (2 Simple Steps)

### **Step 1: Start the Backend** (Open Terminal 1)

**Option A: On macOS/Linux/WSL**
```bash
cd ~/Desktop/Phase2
./run_backend.sh
```

**Option B: On Windows**
```cmd
cd C:\Users\YourUsername\Desktop\Phase2
run_backend.bat
```

**Option C: Manual (All Platforms)**
```bash
cd backend
export DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_gjzWEi0sPM8q@ep-wandering-frost-a7uxtoay-pooler.ap-southeast-2.aws.neon.tech/neondb"
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

✅ You should see:
```
Uvicorn running on http://0.0.0.0:8000
```

---

### **Step 2: Start the Frontend** (Open Terminal 2)

```bash
cd ~/Desktop/Phase2/frontend
npm run dev
```

✅ You should see:
```
▲ Next.js 16.0.0
- Local: http://localhost:3000
```

---

## 🌐 Access Your Application

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend UI** | http://localhost:3000 | Task Management Interface |
| **Backend API** | http://localhost:8000 | REST API Server |
| **API Docs** | http://localhost:8000/docs | Interactive API Documentation |
| **OpenAPI Schema** | http://localhost:8000/openapi.json | API Specification |

---

## 🧪 Test the Integration

### 1. Open Frontend in Browser
```
http://localhost:3000
```

### 2. Create a Task
Click "Add Task" in the UI and fill in:
- **Title**: "My First Task"
- **Description**: "Testing the integration"
- **Due Date**: Pick a date

### 3. Verify in Backend
Open API Docs: http://localhost:8000/docs

Look for your task in the list endpoint response

### 4. Check Neon Database
All data is saved to your Neon PostgreSQL database!

---

## 📊 Database Information

**Database Type**: Neon PostgreSQL (Serverless)
**Tables Created**:
- `users` - User accounts
- `tasks` - User tasks

**Location**: https://console.neon.tech

**Connection String** (in `.env`):
```
postgresql+asyncpg://neondb_owner:npg_gjzWEi0sPM8q@ep-wandering-frost-a7uxtoay-pooler.ap-southeast-2.aws.neon.tech/neondb
```

---

## 🔄 Data Flow

```
Frontend (Next.js)
    ↓
    │ HTTP Requests
    ↓
Backend API (FastAPI)
    ↓
    │ SQL Queries
    ↓
Neon PostgreSQL Database
```

All user tasks are stored in your Neon database automatically!

---

## 🛑 Stop the Services

**Backend** (Terminal 1): Press `Ctrl+C`
**Frontend** (Terminal 2): Press `Ctrl+C`

---

## 🔧 Troubleshooting

### Backend won't start: "Port 8000 already in use"
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn src.main:app --port 8001 --reload
```

### Frontend won't start: "Port 3000 already in use"
```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Backend can't connect to Neon
1. Check `.env` file has correct DATABASE_URL
2. Verify Neon project is active at https://console.neon.tech
3. Check internet connection (Neon requires connection to remote server)

### Frontend can't connect to Backend
1. Check backend is running on port 8000
2. Verify `frontend/.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8000`
3. Check browser console for CORS errors

### "ModuleNotFoundError" in backend
```bash
cd backend
pip install -r requirements.txt
```

### "npm ERR!" in frontend
```bash
cd frontend
npm install
npm install --legacy-peer-deps
```

---

## 📝 Project Structure

```
Phase2/
├── backend/
│   ├── src/
│   │   ├── main.py (FastAPI app)
│   │   ├── database.py (Neon connection)
│   │   ├── models/ (User, Task schemas)
│   │   ├── api/ (Endpoints)
│   │   └── services/ (Business logic)
│   ├── .env (Neon database configuration)
│   └── requirements.txt (Python dependencies)
│
├── frontend/
│   ├── src/
│   │   ├── app/ (Next.js pages)
│   │   ├── components/ (React components)
│   │   └── lib/ (Utilities)
│   ├── .env.local (API configuration)
│   └── package.json (Node dependencies)
│
├── run_backend.sh (Startup script)
├── run_backend.bat (Windows startup)
└── QUICK_START_GUIDE.md (This file)
```

---

## 🎨 Available Endpoints

### Authentication (if set up)
- `POST /api/auth/signup` - Register
- `POST /api/auth/signin` - Login

### Task Management
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks` - List tasks
- `GET /api/{user_id}/tasks/{task_id}` - Get task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `PATCH /api/{user_id}/tasks/{task_id}` - Partial update
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

See **http://localhost:8000/docs** for interactive API explorer

---

## 💡 Tips

1. **Auto-reload**: Backend restarts when you change code (thanks to `--reload`)
2. **Hot refresh**: Frontend refreshes automatically when you save code
3. **API Docs**: Use http://localhost:8000/docs to test endpoints
4. **Neon Console**: View database at https://console.neon.tech
5. **Git**: Commit your work regularly
   ```bash
   git add .
   git commit -m "Your message"
   ```

---

## 🚀 Next Steps

1. **Test the UI**: Create, read, update, delete tasks
2. **Verify Data**: Check tasks are saved to Neon
3. **Explore API**: Visit http://localhost:8000/docs
4. **Deploy**: When ready, deploy to production

---

## 📞 Support

If you encounter issues:

1. Check the error message in the terminal
2. Refer to troubleshooting section above
3. Verify environment variables in `.env` files
4. Check Neon database status at https://console.neon.tech

---

## ✅ Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Can access http://localhost:3000 in browser
- [ ] Can create a task in frontend
- [ ] Task appears in http://localhost:8000/docs list
- [ ] Data persists in Neon database
- [ ] No errors in either terminal

---

**Ready to go! 🎉**

Open two terminals and follow the "How to Run" section above.
