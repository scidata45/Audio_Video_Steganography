StegoVault - Windows setup

1. Open PowerShell inside this folder:
   python -m venv venv
   venv\Scripts\activate
   python -m pip install -r requirements.txt
   python app.py
2. Open http://127.0.0.1:5000

Google Login setup (required to use the account dashboard)
---------------------------------------------------------
Google Login needs OAuth credentials; it will not work until you configure them.

1. In Google Cloud Console, create/select a project and configure the OAuth consent screen.
2. Create an OAuth Client ID of type "Web application".
3. Add this Authorized redirect URI for local development:
   http://127.0.0.1:5000/auth/callback
4. In PowerShell, set the credentials for the current terminal session (replace values):
   $env:GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   $env:GOOGLE_CLIENT_SECRET="your-client-secret"
   $env:STEGOVAULT_SECRET_KEY="replace-with-a-long-random-secret"
5. Run the app in that same terminal:
   python app.py

The SQLite database stegovault.db is created automatically. It stores Google account identifiers and activity metadata (operation, media type, original filename, file size, timestamp and status). It does not store message contents, passwords, or encryption keys. Users can only see their own history.

For deployment, use HTTPS, a strong random STEGOVAULT_SECRET_KEY, secure environment variables, and debug mode off. Never commit OAuth credentials or secret keys to source control. Configure the exact HTTPS callback URI in Google Cloud Console when deployed.

Notes
-----
- Existing audio/video hide and extract routes are retained.
- History is recorded for operations by signed-in users. Guest operations still work but are not associated with an account.
- The current project modules support WAV audio and supported video formats; do not advertise image support unless an image module is implemented.
- Clearing history deletes only activity rows for the signed-in account; it does not delete files previously downloaded by the user.
