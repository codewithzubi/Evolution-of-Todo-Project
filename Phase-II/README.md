# Phase II: Full-Stack Web Todo App

A modern full-stack web application with glassmorphic UI design, JWT authentication, and Neon PostgreSQL database integration.

## 🚀 Features

- **Glassmorphic UI**: Beautiful frosted glass design with vibrant gradients
- **JWT Authentication**: Secure login and registration with token-based auth
- **Task Management**: Full CRUD operations for user tasks
- **Responsive Design**: Works on all device sizes
- **Real-time Updates**: Optimistic UI updates for better user experience

## 🛠️ Tech Stack

- **Frontend**: Next.js 16+, TypeScript, Tailwind CSS v4
- **Backend**: FastAPI, Python 3.13+
- **Database**: Neon PostgreSQL with SQLModel
- **Authentication**: Better Auth with JWT
- **Styling**: Glassmorphism design with custom Tailwind utilities

## 📋 Prerequisites

- Node.js 20+ (for frontend)
- Python 3.13+ (for backend)
- Docker & Docker Compose (for containerized deployment)
- A Neon account (for PostgreSQL database)

## 🔧 Setup Instructions

### Local Development

1. **Clone and navigate to the project:**
   ```bash
   cd phase-ii
   ```

2. **Set up backend:**
   ```bash
   cd backend
   # Create virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   uv pip install -r pyproject.toml  # or use your preferred Python package manager
   ```

3. **Set up frontend:**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run the applications:**
   - **Backend:**
     ```bash
     cd backend
     uvicorn src.main:app --reload
     ```
   - **Frontend:**
     ```bash
     cd frontend
     npm run dev
     ```

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000

## 🏗️ Project Structure

```
phase-ii/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── core/           # Security and configuration
│   │   ├── database/       # Database connection
│   │   ├── models/         # SQLModel definitions
│   │   └── services/       # Business logic
│   └── pyproject.toml      # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # UI components
│   │   │   └── glass/     # Glassmorphic components
│   │   ├── lib/           # API client & auth hooks
│   │   └── styles/        # Tailwind CSS
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Multi-service orchestration
└── .env.example           # Environment variables template
```

## 🚦 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get JWT token

### Tasks
- `GET /tasks/` - Get all user tasks
- `POST /tasks/` - Create a new task
- `GET /tasks/{task_id}` - Get a specific task
- `PUT /tasks/{task_id}` - Update a task
- `PATCH /tasks/{task_id}/status` - Update task status
- `DELETE /tasks/{task_id}` - Delete a task

## 🎨 Glassmorphism Design

The UI features a modern glassmorphic design with:
- Frosted glass cards with backdrop blur
- Vibrant gradient backgrounds
- Smooth animations and transitions
- Responsive layout for all screen sizes

## 🔐 Authentication Flow

1. User registers/login via frontend
2. Backend creates JWT token with user ID
3. Token is stored in frontend and sent with each request
4. Backend middleware verifies JWT and injects current user
5. Tasks are filtered by user ID to ensure data isolation

## 🧪 Testing

Run backend tests:
```bash
cd backend
pytest
```

Run frontend tests:
```bash
cd frontend
npm test
```

## 🚀 Deployment

For production deployment, update the environment variables in `.env` with production values and use the Docker Compose setup or deploy the frontend and backend separately to your preferred hosting platforms.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.