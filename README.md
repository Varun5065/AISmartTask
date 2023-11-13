Installation and setup for running the streamlit application.
•	First create a virtual environment for running the streamlit application.
•	Next set the openai api key for gpt models using the cmd: set OPENAI_API_KEY=key(no ‘’ or “” required)
•	Login into the aismarttask google account. The credentials are:
o	aismarttask@gmail.com
o	aismarttask2023-password
•	Now, open the google cloud console with this account.
•	There go to API & Services and then go to 0Auth Consent screen. Here, make sure to add the test users so that they can access the application.
•	Go to credentials and if none exists create a 0Auth2.0Client ID.
•	Next, download the 0Auth credentials file (already exists) into the directory where the code is present with the name ‘credentials.json’
•	Make sure to add the ‘http://localhost:8501’ in the Authorized JavaScript origins and ‘http://localhost:8080/’ in the  Authorized redirect URL’s.
•	The first URL is the streamlit application running port and the second link is the port number used in the following code: 
•	creds = flow.run_local_server(port=8080)
o	This code is present in the function google_calender_authenticate.
•	So, make sure to change the URL’s based on your port numbers.
•	For email, the 2-step verification is already set up. So please change the mobile number and recovery mail, then create an app password that will be used as sender’s password.
•	After these configurations, start the virtual environment and run the cmd: streamlit run app.py
REFERENCES:
For Google Calender: https://youtu.be/B2E82UPUnOY?si=vrKmuRT8WE1qmyva
For GMAIL setup: https://youtu.be/hXiPshHn9Pw?si=m7yz4FvJBRRbrD9F
DEMO: https://drive.google.com/file/d/1avOcvD7VEQ4NASZwalpNqX5WxX5JqFAF/view?usp=sharing
