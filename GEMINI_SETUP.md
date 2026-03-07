# Google Gemini API Setup Guide

## 🌟 Getting Your Gemini API Key

### Step 1: Get API Key from Google AI Studio

1. **Visit Google AI Studio**
   - Go to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Sign in with Google Account**
   - Use your Google account to sign in

3. **Create API Key**
   - Click "Create API Key" button
   - Select your Google Cloud project (or create a new one)
   - Copy the generated API key

### Step 2: Configure Your Application

1. **Create .env file** (if not exists)
   ```bash
   copy .env.example .env
   ```

2. **Add your API key to .env**
   ```bash
   GEMINI_API_KEY=your_actual_api_key_here
   AI_MODEL=gemini
   ```

3. **Save the file**

### Step 3: Install Gemini SDK

```bash
pip install google-generativeai
```

Or reinstall all requirements:
```bash
pip install -r requirements.txt
```

### Step 4: Restart the Application

```bash
# Stop current app (Ctrl+C in terminal)
# Then restart:
streamlit run app.py
```

## ✨ Using Gemini in the App

Once configured, you'll see a toggle in the sidebar:

- **"Use Google Gemini API"** - Toggle ON to use Gemini
- **Status indicator** - Shows which AI model is active
  - ✨ Using Gemini API (Enhanced)
  - 🔧 Using Local Models (BLIP)

## 🆚 Gemini vs Local Models

| Feature | Google Gemini | Local BLIP |
|---------|---------------|------------|
| **Quality** | ⭐⭐⭐⭐⭐ Superior | ⭐⭐⭐⭐ Good |
| **Speed** | Fast (API call) | Slower (local processing) |
| **Cost** | Free tier available | Free (no API) |
| **Internet** | Required | Not required |
| **Setup** | API key needed | No setup |
| **Captions** | More creative | Template-based |
| **Analysis** | More detailed | Standard |

## 💰 Gemini API Pricing

- **Free Tier**: 60 requests per minute
- **Paid Tier**: Available for higher usage
- Check current pricing: https://ai.google.dev/pricing

## 🔧 Troubleshooting

### API Key Not Working
```
Error: Gemini API key not found
```
**Solution**: Make sure .env file exists and contains `GEMINI_API_KEY=your_key`

### Import Error
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solution**: Install the package
```bash
pip install google-generativeai
```

### API Rate Limit
```
Error: Resource exhausted
```
**Solution**: You've exceeded free tier limits. Wait a minute or upgrade to paid tier.

## 📚 Additional Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Google AI Studio**: https://aistudio.google.com
- **Pricing**: https://ai.google.dev/pricing
- **Support**: https://ai.google.dev/support

## 🎯 Quick Start Example

1. Get API key from https://makersuite.google.com/app/apikey
2. Add to .env: `GEMINI_API_KEY=your_key_here`
3. Restart app: `streamlit run app.py`
4. Toggle "Use Google Gemini API" in sidebar
5. Upload image and generate!

---

**Note**: The app works perfectly fine without Gemini API using local BLIP models. Gemini is optional for enhanced quality!
