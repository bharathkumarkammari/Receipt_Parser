# Deployment Notes for Receipt App

## Changes Made for Deployment

The following changes have been made to `app.py` to remove dependencies on local files:

### 1. Removed .env Dependencies
- Commented out `from dotenv import load_dotenv`
- Commented out `load_dotenv()` call
- All environment variables are now read directly from system environment

### 2. Removed service_account.json Dependencies
- Added `get_google_sheets_client()` function that can use either:
  - Environment variable `GOOGLE_SERVICE_ACCOUNT_JSON` (for deployment)
  - Local `service_account.json` file (for local development)
- Added proper error handling when Google Sheets is not configured

### 3. Updated Functions
- `load_receipts_from_gsheet()`: Now handles case where sheet is None
- `upload_file()`: Checks if sheet is configured before uploading
- `upload_to_gsheet()`: Validates sheet configuration before proceeding

## Environment Variables Required in Render

Set these environment variables in your Render dashboard:

### Required Variables
```
SESSION_SECRET=your_random_secret_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
POWERBI_PUBLIC_EMBED_URL=your_powerbi_embed_url
```

### Google Sheets Configuration
```
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
GOOGLE_SHEET_NAME=Costco_Input
GOOGLE_WORKSHEET_NAME=Sheet1
```

### Power BI Configuration (Optional)
```
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret
POWERBI_WORKSPACE_ID=your_workspace_id
POWERBI_DATASET_ID=your_dataset_id
```

## How to Get GOOGLE_SERVICE_ACCOUNT_JSON

1. Download your `service_account.json` file from Google Cloud Console
2. Open the file and copy the entire JSON content
3. Paste it as the value for `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable in Render
4. Make sure to include the entire JSON object, including the curly braces

## Local Development

For local development, you can still use:
- `.env` file (uncomment the dotenv lines in app.py)
- `service_account.json` file in the project root

## Deployment Checklist

- [ ] Set all required environment variables in Render
- [ ] Ensure Google Sheet is shared with the service account email
- [ ] Test the application after deployment
- [ ] Verify Google Sheets integration works
- [ ] Check Power BI refresh functionality (if configured)

## Troubleshooting

### Google Sheets Not Working
- Check that `GOOGLE_SERVICE_ACCOUNT_JSON` is properly set
- Verify the service account has access to the Google Sheet
- Check that `GOOGLE_SHEET_NAME` and `GOOGLE_WORKSHEET_NAME` are correct

### Power BI Not Working
- Verify all Power BI environment variables are set
- Check that the service principal has proper permissions
- Ensure the Power BI admin settings are configured correctly

### General Issues
- Check Render logs for detailed error messages
- Verify all environment variables are set correctly
- Test locally first to ensure the code works 