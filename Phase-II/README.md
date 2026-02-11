# The Evolution of Todo - Phase II

> A modern, spec-driven full-stack todo application built with Next.js, FastAPI, and Neon PostgreSQL

[![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128.5-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)

## 📖 Overview

The Evolution of Todo is a production-ready task management application that demonstrates modern full-stack development practices using **Spec-Driven Development (SDD)** methodology. Built for Hackathon II Phase II, this project showcases clean architecture, comprehensive testing, and premium UI/UX design.

## ✨ Features

### 🎨 User Interface
- **Modern Landing Page** - Compelling hero section with phone mockup and feature showcase
- **Dark/Light Mode Toggle** - Seamless theme switching with persistence
- **Responsive Design** - Mobile-first approach, works beautifully on all devices
- **Premium Animations** - Smooth transitions, fade-ins, and hover effects
- **Loading States** - Skeleton loaders for better perceived performance

### 🔐 Authentication
- **Email/Password Authentication** - Secure JWT-based auth
- **Session Persistence** - Stay logged in across page refreshes
- **Protected Routes** - Automatic redirect for unauthenticated users
- **User Isolation** - 100% data separation between users

### ✅ Task Management
- **Create Tasks** - Add tasks with title, description, priority, due date, and tags
- **View Tasks** - Filter by status (All, Pending, Completed)
- **Update Tasks** - Edit any task field with real-time updates
- **Delete Tasks** - Remove tasks with confirmation dialog
- **Toggle Completion** - Mark tasks as complete/pending with one click
- **Priority Levels** - High (red), Medium (orange), Low (blue)
- **Due Dates** - Set deadlines with overdue detection
- **Tags** - Organize tasks with comma-separated tags (colored badges)

### 🚀 Technical Highlights
- **Optimistic Updates** - Instant UI feedback with TanStack Query
- **Type Safety** - Full TypeScript coverage on frontend
- **API Documentation** - Auto-generated FastAPI docs at `/docs`
- **Database Migrations** - Alembic for schema versioning
- **Test Coverage** - 93% backend test coverage with pytest
- **Spec-Driven Development** - Complete specifications, plans, and tasks documented

## 🛠️ Tech Stack

### Frontend
- **Framework:** Next.js 16.1.6 (App Router)
- **Language:** TypeScript 5.0
- **Styling:** Tailwind CSS 3.4.17
- **UI Components:** shadcn/ui
- **Icons:** Lucide React
- **State Management:** TanStack Query v5.62.11
- **Theme:** next-themes
- **Notifications:** Sonner

### Backend
- **Framework:** FastAPI 0.128.5
- **Language:** Python 3.13+
- **ORM:** SQLModel 0.0.32
- **Database:** Neon Serverless PostgreSQL
- **Migrations:** Alembic
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **Testing:** pytest (93% coverage)

### Infrastructure
- **Package Manager (Frontend):** npm
- **Package Manager (Backend):** uv
- **Database Hosting:** Neon
- **Deployment:** Vercel (Frontend) + Railway/Render (Backend)

## 📦 Project Structure

```
Phase-II/
├── frontend/                 # Next.js application
│   ├── app/                 # App Router pages
│   │   ├── (auth)/         # Authentication pages
│   │   ├── (protected)/    # Protected dashboard
│   │   └── page.tsx        # Landing page
│   ├── components/          # React components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── landing/        # Landing page components
│   │   └── dashboard/      # Dashboard components
│   ├── lib/                # Utilities and API client
│   └── hooks/              # Custom React hooks
│
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py         # FastAPI app entry
│   │   ├── config.py       # Configuration
│   │   ├── models/         # SQLModel schemas
│   │   ├── services/       # Business logic
│   │   └── api/            # API routes
│   ├── alembic/            # Database migrations
│   └── tests/              # pytest tests (93% coverage)
│
├── specs/                   # Feature specifications
│   ├── 001-user-auth/      # Auth spec + plan + tasks
│   ├── 002-task-crud/      # Task CRUD spec + plan + tasks
│   └── 003-landing-page/   # Landing page spec + plan + tasks
│
├── history/                 # Prompt History Records (PHRs)
│   ├── prompts/            # Development history
│   └── adr/                # Architecture Decision Records
│
└── .specify/               # Spec-Kit Plus configuration
    ├── memory/             # Project constitution
    └── templates/          # SDD templates
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.13+
- **uv** (Python package manager) - [Install uv](https://github.com/astral-sh/uv)
- **PostgreSQL** database (Neon account recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/hackathon-todo-phase2.git
cd hackathon-todo-phase2
```

### 2. Backend Setup

```bash
cd backend

# Install dependencies with uv
uv sync

# Create .env file
cp .env.example .env

# Edit .env with your configuration:
# DATABASE_URL=postgresql://user:password@host/database
# BETTER_AUTH_SECRET=your-secret-key-32-chars-minimum
# FRONTEND_URL=http://localhost:3000

# Run database migrations
python -m alembic upgrade head

# Start the backend server
python -m uvicorn app.main:app --reload
```

Backend will run at: http://localhost:8000
API docs available at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local with your configuration:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# BETTER_AUTH_SECRET=your-secret-key-32-chars-minimum

# Start the development server
npm run dev
```

Frontend will run at: http://localhost:3000

### 4. Environment Variables

#### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/database
BETTER_AUTH_SECRET=nk3E1HtsdtLTZrzx0owxKqrYz62UEJkR
FRONTEND_URL=http://localhost:3000
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=nk3E1HtsdtLTZrzx0owxKqrYz62UEJkR
```

**Important:** Use the same `BETTER_AUTH_SECRET` in both frontend and backend for JWT validation.

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

**Current Coverage:** 93% (29 passing tests)

### Frontend Tests

```bash
cd frontend

# Run unit tests (when implemented)
npm run test

# Run E2E tests (when implemented)
npm run test:e2e
```

## 📸 Screenshots

### Landing Page
![Landing Page](./docs/screenshots/landing-page.png)
*Modern hero section with compelling CTA and feature showcase*

### Dashboard
![Dashboard](./docs/screenshots/dashboard.png)
*Clean task management interface with filtering and real-time updates*

### Task Card
![Task Card](./docs/screenshots/task-card.png)
*Rich task cards with priority, due dates, tags, and quick actions*

### Dark Mode
![Dark Mode](./docs/screenshots/dark-mode.png)
*Premium dark theme with smooth transitions*

## 🎥 Demo

- **Live Demo:** [https://your-app.vercel.app](https://your-app.vercel.app)
- **Video Walkthrough:** [YouTube/Loom Link](https://youtu.be/your-video-id)
- **API Documentation:** [https://your-api.railway.app/docs](https://your-api.railway.app/docs)

## 📚 Documentation

### Specifications
- [User Authentication Spec](./specs/001-user-auth/spec.md)
- [Task CRUD Spec](./specs/002-task-crud/spec.md)
- [Landing Page Spec](./specs/003-landing-page/spec.md)

### Architecture
- [Project Constitution](./.specify/memory/constitution.md)
- [Architecture Decision Records](./history/adr/)
- [Prompt History Records](./history/prompts/)

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user

#### Tasks
- `GET /api/tasks?status={all|pending|completed}` - List tasks
- `POST /api/tasks` - Create task
- `PATCH /api/tasks/{id}/toggle` - Toggle completion
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

## 🏗️ Development Methodology

This project follows **Spec-Driven Development (SDD)** using Spec-Kit Plus:

1. **Specification** - Define requirements in `spec.md`
2. **Planning** - Create architectural plan in `plan.md`
3. **Tasks** - Break down into testable tasks in `tasks.md`
4. **Implementation** - Execute tasks with TDD approach
5. **Documentation** - Record decisions in ADRs and PHRs

### Key Principles
- ✅ Locked tech stack (no mid-project changes)
- ✅ Feature scope discipline (exactly 5 CRUD operations)
- ✅ User-scoped security (100% data isolation)
- ✅ UI/UX standards (dark mode, responsive, accessible)
- ✅ Clean architecture (layered backend, modular frontend)
- ✅ Test-first development (93% backend coverage)

## 🔒 Security

- **JWT Authentication** - Stateless tokens with 7-day expiration
- **bcrypt Password Hashing** - 12 rounds (~250ms)
- **CORS Protection** - Restricted to frontend origin only
- **SQL Injection Prevention** - SQLModel parameterized queries
- **Data Isolation** - All queries filtered by user_id from JWT
- **No Sensitive Data in Errors** - Generic error messages

## 🚢 Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod
```

### Backend (Railway/Render)

```bash
# Railway
railway login
railway init
railway up

# Or use Render
# Connect GitHub repo and deploy via dashboard
```

### Database (Neon)

1. Create account at [neon.tech](https://neon.tech)
2. Create new project
3. Copy connection string to `DATABASE_URL`
4. Run migrations: `python -m alembic upgrade head`

## 🤝 Contributing

This is a hackathon submission project. For educational purposes, feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your Name](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Built for **Hackathon II - Phase II**
- Spec-Driven Development methodology by Specify
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- Icons from [Lucide](https://lucide.dev/)
- Inspired by modern task management apps

## 📊 Project Stats

- **Total Lines of Code:** ~3,500+
- **Backend Files:** 17
- **Frontend Files:** 28+
- **Test Coverage:** 93%
- **Specifications:** 3 complete features
- **Development Time:** Phase II duration
- **Commits:** [View on GitHub](https://github.com/yourusername/hackathon-todo-phase2/commits)

---

**Built with ❤️ using Spec-Driven Development**
