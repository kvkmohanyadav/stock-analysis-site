# How to Push Code to GitHub

## Option 1: If this is NOT yet a git repository

1. **Initialize git repository:**
   ```bash
   git init
   ```

2. **Create a .gitignore file** (important for Python/Node projects):
   ```bash
   echo "backend/__pycache__/
   backend/venv/
   backend/.env
   backend/cache/
   backend/*.db
   node_modules/
   .env
   .vscode/
   *.log" > .gitignore
   ```

3. **Add all files:**
   ```bash
   git add .
   ```

4. **Commit:**
   ```bash
   git commit -m "Initial commit"
   ```

5. **Add remote repository** (after creating one on GitHub):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-site.git
   ```

6. **Push to GitHub:**
   ```bash
   git push -u origin main
   ```
   (Use `master` instead of `main` if your default branch is master)

## Option 2: If this IS already a git repository

1. **Check current status:**
   ```bash
   git status
   ```

2. **Add and commit any changes:**
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

3. **Check if remote is configured:**
   ```bash
   git remote -v
   ```

4. **If no remote, add one:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-site.git
   ```

5. **Push to GitHub:**
   ```bash
   git push -u origin main
   ```
   (Use `master` instead of `main` if that's your branch name)

## Steps to Create a New Repository on GitHub

1. Go to https://github.com and log in
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Name it: `stock-analysis-site`
5. Choose public or private
6. **DO NOT** initialize with README, .gitignore, or license (since you already have code)
7. Click **"Create repository"**
8. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/stock-analysis-site.git`)

## Authentication Options

### Option A: HTTPS with Personal Access Token
- GitHub no longer accepts passwords
- Create a Personal Access Token:
  1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token
  3. Give it permissions: `repo` (full control)
  4. Use token as password when prompted

### Option B: SSH (Recommended)
```bash
git remote set-url origin git@github.com:YOUR_USERNAME/stock-analysis-site.git
```

## Quick Command Summary

```bash
# Check if git is initialized
git status

# Initialize git (if needed)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Add remote (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/stock-analysis-site.git

# Push to GitHub
git push -u origin main
```

## Need Help?

If you encounter errors:
- "fatal: not a git repository" → Run `git init`
- "fatal: remote origin already exists" → Use `git remote remove origin` first, or use `git remote set-url`
- "Authentication failed" → Use a Personal Access Token or set up SSH
- "Permission denied" → Check your GitHub username and token/SSH key
