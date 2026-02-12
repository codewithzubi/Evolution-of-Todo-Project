# Deploy Backend to Hugging Face Spaces

## Prerequisites
- Hugging Face account (free)
- Git installed
- Backend code with Dockerfile ready ✅

## Step 1: Create a New Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in details:
   - **Space name:** `evolution-of-todo-backend` (or your choice)
   - **License:** MIT
   - **Space SDK:** Docker
   - **Visibility:** Public (or Private)
4. Click "Create Space"

## Step 2: Push Backend Code to HF Space

```bash
# Navigate to backend directory
cd backend

# Add HF Space as remote (replace USERNAME and SPACE_NAME)
git remote add hf https://huggingface.co/spaces/USERNAME/SPACE_NAME

# Push backend files to HF Space
git subtree push --prefix=backend hf main

# Or if you want to push the entire repo:
# git push hf 003-landing-page:main
```

**Alternative: Direct Upload via Web UI**
1. Go to your Space's "Files" tab
2. Upload these files from `backend/` folder:
   - `Dockerfile`
   - `requirements.txt`
   - `.dockerignore`
   - `alembic.ini`
   - Entire `app/` folder
   - Entire `alembic/` folder

## Step 3: Configure Environment Variables

1. Go to your Space's "Settings" tab
2. Scroll to "Repository secrets"
3. Add these secrets:

```
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech/database?sslmode=require

BETTER_AUTH_SECRET=your-32-character-secret-key-here

OPENAI_API_KEY=sk-your-openai-api-key-here

OPENAI_MODEL=gpt-4

FRONTEND_URL=https://your-frontend-url.vercel.app
```

**Important:**
- Use your actual Neon database connection string for `DATABASE_URL`
- Generate a secure 32+ character secret for `BETTER_AUTH_SECRET`
- Add your OpenAI API key for Phase-III chat functionality
- Update `FRONTEND_URL` after deploying frontend to Vercel

## Step 4: Wait for Build

- HF Spaces will automatically build your Docker container
- Build time: ~5-10 minutes
- Check "Logs" tab for build progress
- Once built, your API will be live at: `https://USERNAME-SPACE_NAME.hf.space`

## Step 5: Test Your Deployment

```bash
# Health check
curl https://USERNAME-SPACE_NAME.hf.space/health

# API docs
# Visit: https://USERNAME-SPACE_NAME.hf.space/docs
```

## Step 6: Update Frontend Configuration

After backend is deployed, update your frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=https://USERNAME-SPACE_NAME.hf.space
```

## Troubleshooting

### Build Fails
- Check "Logs" tab for error messages
- Verify Dockerfile syntax
- Ensure requirements.txt has all dependencies

### Database Connection Issues
- Verify DATABASE_URL is correct in secrets
- Check Neon database is active
- Test connection from local machine first

### CORS Errors
- Verify FRONTEND_URL in secrets matches your Vercel URL
- Check CORS configuration in `app/main.py`
- Clear browser cache and try again

### Port Issues
- HF Spaces expects port 7860 (already configured in Dockerfile)
- Don't change the port in CMD

## Updating Your Deployment

```bash
# Make changes to code
# Commit changes
git add .
git commit -m "Update backend"

# Push to HF Space
git subtree push --prefix=backend hf main
```

## Free Tier Limits

Hugging Face Spaces free tier:
- ✅ 2 vCPU
- ✅ 16GB RAM
- ✅ 50GB storage
- ✅ Always-on (no sleep)
- ✅ Custom domains

Perfect for this project!

## Alternative: Railway Deployment

If you prefer Railway:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Deploy
railway up

# Add environment variables via dashboard
```

---

**Your backend will be live at:** `https://USERNAME-SPACE_NAME.hf.space`

**API Documentation:** `https://USERNAME-SPACE_NAME.hf.space/docs`
