# 🚀 Vercel Deployment Guide

## Quick Deploy (3 minutes)

### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub

2. **Import Project:**
   - Click "Add New..." → "Project"
   - Select your GitHub repository: `Sounds-true/pas_in_peace`
   - Click "Import"

3. **Configure Project:**
   ```
   Framework Preset: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **Environment Variables:**
   Add these in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.vercel.app
   NEXT_PUBLIC_TELEGRAM_BOT_USERNAME=pas_in_peace_bot
   NEXT_PUBLIC_QUEST_BUILDER_ENABLED=true
   NEXT_PUBLIC_ANALYTICS_ENABLED=true
   NEXT_PUBLIC_LETTER_MANAGER_ENABLED=true
   ```

5. **Deploy!** Click "Deploy"

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from root directory
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? [Your account]
# - Link to existing project? No
# - Project name: pas-in-peace
# - In which directory is your code? ./frontend
# - Override settings? No
```

## Post-Deploy

After deployment, you'll get a URL like:
```
https://pas-in-peace-xyz.vercel.app
```

### Pages to check:
- `/` - Landing page
- `/login` - Telegram auth (will need real bot)
- `/demo` - All Liquid Glass components
- `/dashboard` - Main dashboard (requires auth)

### Known Limitations (without backend):
- Authentication won't work (needs real Telegram bot + backend API)
- API calls will fail (needs backend deployed)
- Demo page will work perfectly! ✅

## Deploy Backend Later

When ready to deploy backend:
1. Use Vercel Serverless Functions or
2. Deploy to Railway/Render/Fly.io
3. Update `NEXT_PUBLIC_API_URL` in Vercel env vars

## Troubleshooting

**Build fails?**
- Check Node version (should be 18+)
- Ensure all dependencies in package.json

**Pages not loading?**
- Check Vercel deployment logs
- Verify build completed successfully

**404 errors?**
- Next.js handles routing automatically
- Check file names match routes

## Continuous Deployment

Vercel automatically redeploys on:
- Push to `main` branch
- Push to any branch (creates preview URL)

Preview URLs format:
```
https://pas-in-peace-git-[branch-name]-[your-account].vercel.app
```

---

Made with ❤️ for parents reconnecting with their children
