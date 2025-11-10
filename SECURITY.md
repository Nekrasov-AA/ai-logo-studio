# Security Guidelines for AI Logo Studio

## API Key Management

### 🔐 Important Security Rules

1. **NEVER commit API keys to git**
2. **Use environment variables only**
3. **Don't share your .env files**
4. **Regularly rotate your API keys**

### 🔧 Setup Instructions

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Get your API keys:**
   - **OpenAI**: Visit https://platform.openai.com/api-keys
   - **Stability AI**: Visit https://platform.stability.ai/account/keys

3. **Edit .env file with your real keys:**
   ```bash
   # Edit the .env file (never commit this!)
   nano .env
   ```

4. **Verify .env is ignored by git:**
   ```bash
   git status
   # .env should NOT appear in the list
   ```

### 📁 File Structure

```
ai-logo-studio/
├── .env.example          # ✅ Safe - template file (committed)
├── .env                  # ❌ NEVER commit - contains real keys
├── .gitignore           # ✅ Ensures .env is ignored
└── ...
```

### 🚨 What to Do If You Accidentally Commit an API Key

1. **Immediately revoke the exposed key** from the provider's dashboard
2. **Generate a new API key**
3. **Update your .env file** with the new key
4. **Consider git history cleanup** (git filter-branch or BFG)

### 🔍 How API Keys Are Used

The application loads API keys from environment variables:

```python
# In worker/src/ai_engines/openai_provider.py
api_key = os.getenv("OPENAI_API_KEY")

# In worker/src/ai_engines/stability_provider.py  
api_key = os.getenv("STABILITY_API_KEY")
```

### 🛡️ Additional Security Measures

- API keys are never logged
- Keys are only stored in memory during execution
- All AI provider communication uses HTTPS
- Rate limiting prevents API abuse
- Timeout protection prevents resource exhaustion

### 📊 Environment Variables Reference

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `OPENAI_API_KEY` | OpenAI DALL-E 3 access | `sk-...` | No* |
| `STABILITY_API_KEY` | Stability AI access | `sk-...` | No* |
| `USE_NEW_AI` | Enable AI providers | `true` | No |

*At least one AI provider key is required for full functionality

### 🔄 Key Rotation Best Practices

1. **Rotate keys monthly** for production
2. **Use different keys** for development/staging/production
3. **Monitor API usage** for suspicious activity
4. **Set spending limits** on provider dashboards

### 🚫 What NOT to Do

- ❌ Don't put API keys in code comments
- ❌ Don't share keys in Slack/email
- ❌ Don't use the same key across multiple projects
- ❌ Don't commit .env files
- ❌ Don't screenshot or log API keys