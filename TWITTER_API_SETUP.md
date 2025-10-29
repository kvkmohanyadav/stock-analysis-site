# Twitter API v2 Setup Guide

This application uses Twitter API v2 to fetch real tweets from specified handles. Follow these steps to set up:

## Prerequisites

1. A Twitter Developer Account
2. A Twitter App created in the Developer Portal

## Steps to Get Twitter API Bearer Token

### Step 1: Create a Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal)
2. Sign up or log in with your Twitter account
3. Complete the application form (if needed)

### Step 2: Create a Twitter App

1. Go to [Twitter Developer Dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Click "Create App" or "Create Project"
3. Fill in the required information:
   - App name: e.g., "Stock Analysis App"
   - Use case: Select appropriate use case
   - App permissions: Read-only is sufficient for fetching tweets

### Step 3: Generate Bearer Token

1. After creating the app, go to the "Keys and Tokens" tab
2. Under "Bearer Token", click "Generate" or "Regenerate"
3. Copy the Bearer Token (starts with `AAAAAAAAAAAAAAAAAAA...`)

⚠️ **Important**: Keep your Bearer Token secure and never commit it to version control!

## Step 4: Set Environment Variable

### Windows PowerShell:
```powershell
$env:TWITTER_BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"
```

### Windows Command Prompt (CMD):
```cmd
set TWITTER_BEARER_TOKEN=YOUR_BEARER_TOKEN_HERE
```

### For Permanent Setup (Windows):
1. Open System Properties → Environment Variables
2. Under "User variables", click "New"
3. Variable name: `TWITTER_BEARER_TOKEN`
4. Variable value: Your Bearer Token
5. Click OK

### Linux/Mac:
```bash
export TWITTER_BEARER_TOKEN="YOUR_BEARER_TOKEN_HERE"
```

To make it permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export TWITTER_BEARER_TOKEN="YOUR_BEARER_TOKEN_HERE"' >> ~/.bashrc
source ~/.bashrc
```

## Step 5: Restart Backend Server

After setting the environment variable, restart your Flask backend:

1. Stop the current backend server (Ctrl+C)
2. Restart it:
   ```powershell
   cd backend
   python app.py
   ```

## Testing

1. Search for a stock (e.g., TCS, INFY, RELIANCE)
2. The tweets section should now display real tweets from:
   - @REDBOXINDIA
   - @ETMarkets
3. Tweets mentioning the stock symbol will be shown

## API Rate Limits

Twitter API v2 has rate limits:
- **Free tier**: 10,000 tweets per month for search
- **Recent Search endpoint**: 180 requests per 15-minute window per user

If you hit rate limits, you'll see an error message in the backend logs.

## Troubleshooting

- **"Bearer Token not configured"**: Make sure the environment variable is set correctly
- **"Authentication failed"**: Check that your Bearer Token is valid and not expired
- **"Rate limit exceeded"**: Wait 15 minutes or upgrade your Twitter API plan
- **No tweets found**: The handles may not have tweeted about that stock recently

## Security Notes

- Never share your Bearer Token publicly
- Don't commit tokens to Git repositories
- Consider using a `.env` file with `python-dotenv` for local development (future enhancement)

