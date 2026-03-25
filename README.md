# SpendLens

SpendLens is a smart spending tracker that securely connects to your Gmail, finds recent payment and receipt emails, and automatically extracts transaction details—amount, sender, date, and subject—so you can see your spending at a glance without manually reading every message.

## Features

- 🔐 **Secure Google OAuth Login** – Connect your Gmail account safely
- 📧 **Email Scanning** – Automatically finds transaction-related emails (debit, credit, receipts, invoices, transfers)
- 💰 **Amount Extraction** – Uses regex to detect amounts in multiple currency formats (₦, $, N, etc.)
- 📅 **Date & Metadata** – Captures sender, date, and subject for each transaction
- 🎨 **React Frontend** – Clean, intuitive UI to view your spending data
- ⚡ **FastAPI Backend** – Fast, modern Python API with Gmail integration

## Tech Stack

- **Backend**: FastAPI, Google API Client, Python
- **Frontend**: React, Vite, Fetch API
- **Authentication**: Google OAuth 2.0
- **Email Parsing**: BeautifulSoup, Regex (with PKCE support)

## Project Structure

```
spendlens/
├── main.py                      # FastAPI app entry point
├── router/
│   ├── gmail.py                # Gmail scanning and amount extraction endpoints
│   └── setup.py               # OAuth authentication routes
├── utils/
│   ├── auth.py                # OAuth flow and token management
│   ├── credentials.json        # Google OAuth credentials (add yours)
│   ├── gmail_auth.py          # Gmail service initialization
│   └── email_cleaning.py      # Email parsing and regex extraction
├── token.json                  # Generated after first OAuth login
└── frontend/                   # React Vite app (create separately)
    ├── src/
    │   ├── App.jsx
    │   └── components/
    └── package.json
```

## Setup Instructions

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/dammyolujobi/spendlens.git
   cd spendlens
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # OR
   source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install fastapi uvicorn google-auth-oauthlib google-auth-httplib2 google-api-python-client beautifulsoup4
   ```

4. **Set up Google OAuth**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Gmail API
   - Create an OAuth 2.0 credential (Desktop app)
   - Download the credentials JSON and place it at `utils/credentials.json`

5. **Run the backend**
   ```bash
   python main.py
   ```
   Backend will start at `http://localhost:8000`

### Frontend Setup

1. **Create a Vite React app**
   ```bash
   npm create vite@latest frontend -- --template react
   cd frontend
   npm install
   ```

2. **Run the frontend dev server**
   ```bash
   npm run dev
   ```
   Frontend will start at `http://localhost:3000`

## API Endpoints

### Authentication
- **`GET /setup/auth/login`** – Redirects to Google login
- **`GET /setup/auth/callback`** – OAuth callback (automatic redirect after login)
- **`GET /setup/auth/status`** – Check if user is authenticated

### Spending Data
- **`GET /gmail/spendings`** – Fetch all spending-related emails
  ```json
  {
    "total_found": 2,
    "emails": [
      {
        "subject": "Your Jumia Order",
        "from": "jumia@jumia.com",
        "date": "Wed, 24 Sep 2025 21:52:43 +0000",
        "content": "Cleaned email body text"
      }
    ]
  }
  ```

- **`GET /gmail/get_amount`** – Fetch emails with extracted amounts
  ```json
  [
    {
      "from": "jumia",
      "amount": "30426.5",
      "date": "Wed, 24 Sep 2025 21:52:43 +0000",
      "subject": "Your Jumia Order - 1437119912"
    }
  ]
  ```

## Configuration

### CORS Settings
The backend includes CORS middleware configured for `http://localhost:3000`. To allow other origins, modify [main.py](main.py):

```python
allow_origins=["http://localhost:3000", "http://example.com"]
```

### Email Search Query
To customize which emails are scanned, modify the query in [router/gmail.py](router/gmail.py):

```python
q="subject:(debit OR credit OR receipt OR payment OR invoice OR transaction OR transfer)"
```

### Amount Extraction Patterns
Regex patterns for amount extraction are in [utils/email_cleaning.py](utils/email_cleaning.py). Supported formats:
- Naira: `₦ 1,250.50` or `N 1,250.50`
- Dollar: `$ 100.00`
- Named amounts: `Credit Amount 500` or `Debit Amount 200`

## Usage

1. **Start both servers**
   ```bash
   # Terminal 1: Backend
   python main.py

   # Terminal 2: Frontend
   npm run dev
   ```

2. **Open the app** at `http://localhost:3000`

3. **Click "Login with Google"** to authenticate

4. **View your spending data** – The app fetches recent transactions from your Gmail

## Security Notes

- ✅ OAuth credentials are stored securely using Google's OAuth flow
- ✅ No passwords are stored—only OAuth tokens
- ✅ Token is refreshed automatically when expired
- ⚠️ Keep `credentials.json` and `token.json` private (add to `.gitignore`)
- ⚠️ For production, use environment variables for sensitive data

## Troubleshooting

### CORS Error
If you see "CORS policy blocked", check that:
- Backend CORS middleware includes your frontend origin
- Backend is running on `http://0.0.0.0:8000`

### "Not authenticated" Error
- Click "Login with Google" first
- Ensure `token.json` was created after login
- Check token hasn't expired (refresh token if needed)

### No Emails Found
- Ensure emails with "debit", "credit", "receipt", etc. in the subject exist
- Check Gmail account access is granted
- Verify search query in [router/gmail.py](router/gmail.py)

## Future Features

- 📊 Spending analytics and charts
- 🏷️ Category tagging (Food, Transport, etc.)
- 📈 Monthly/weekly spending reports
- 🔔 Budget alerts
- 💾 Data export (CSV, PDF)
- 🌐 Multi-currency support

## License

MIT License – feel free to use and modify

## Contributing

Feel free to fork, report issues, and submit pull requests!

## Contact

For questions or feedback, reach out to [@dammyolujobi](https://github.com/dammyolujobi)
