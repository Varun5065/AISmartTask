
# Streamlit Application Setup Instructions

This document provides detailed instructions for setting up and running a Streamlit application with Google Calendar and Gmail integrations.

## Environment Setup

1. **Create a Virtual Environment:**
   - It's recommended to create a virtual environment for running the Streamlit application to manage dependencies effectively.
   - Use the following commands:
     ```
     python -m venv venv
     venv\Scripts\activate
     ```

2. **Set OpenAI API Key:**
   - Use the following command to set the OpenAI API key (replace `key` with your actual API key):
     ```
     set OPENAI_API_KEY=key
     ```
   - Note: Do not use quotes around the key.

3. **Run the requirements.txt file:**
   - Run the requirements file after setting up the virtual environment with:
     ```
     pip install -r requirements.txt
     ```

## Google Account Login

1. **Access Google Cloud Console:**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/) and login with the above credentials.

2. **Configure OAuth Consent Screen:**
   - Go to **API & Services > OAuth Consent Screen**.
   - Add test users to allow them access to the application.

3. **Manage OAuth 2.0 Client ID:**
   - Go to **Credentials**.
   - If a Client ID doesn't exist, create an OAuth 2.0 Client ID.
   - Download the OAuth credentials file into the directory with your code, named `credentials.json`.

4. **Set Authorized URLs:**
   - Add `http://localhost:8501` to Authorized JavaScript origins.
   - Add `http://localhost:8080/` to Authorized redirect URLs.
   - Note: Adjust the URLs based on your port numbers. The first URL is the application running URL, and the second URL is the redirection URL.

5. **Configure Google Calendar Authentication:**
   - The code `creds = flow.run_local_server(port=8080)` is used in `google_calender_authenticate()` function.
   - Ensure the port numbers match with the Authorized redirect URLs.

6. **Email Setup:**
   - 2-step verification is already set up.
   - Change the mobile number and recovery email.
   - Create an app password to be used as the sender's password.

## Running the Application

- Activate the virtual environment.
- Run the application with the command:
  ```
  streamlit run app.py
  ```

## Test Users

- Ensure that the email addresses of test users are added to the Test Users list in the OAuth consent screen.

## References

- For Google Calendar: [Tutorial Video](https://youtu.be/B2E82UPUnOY?si=vrKmuRT8WE1qmyva)
- For Gmail Setup: [Tutorial Video](https://youtu.be/hXiPshHn9Pw?si=m7yz4FvJBRRbrD9F)
- Demo-1 (Setting Up): [Tutorial Video](https://drive.google.com/file/d/1owg3PHNISUI-poDhJFn76D4X98yHOvFr/view?usp=sharing) (until 3:20)
- Demo-2 (Working): [Tutorial Video](https://drive.google.com/file/d/1oNJbhG681nk8AxJuxUBFGfdO3ms3o5OS/view?usp=sharing)
