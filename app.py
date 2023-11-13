import streamlit as st
import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from datetime import datetime, timedelta

# Set up your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
conversation = []
system_message = {
    "role": "system",
    "content": "You are AISmartTask: An innovative AI-driven task management solution tailored for coders or anyone who likes to manage daily routines. You offer an intuitive user experinece by creating a creative summary based on the user inputs:task, priority, and deadline that will be added to their calender. You should print the template as summary:. No extra info like confirmation should be in the result"
    # The rest of the system message...
}
conversation.append(system_message)

# Function to authenticate and create a Google Calendar service
def google_calendar_authenticate():
    creds = None
    # Check if token.json exists and has valid content
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar'])
        except Exception as e:
            st.error(f"Error loading credentials from token.json: {e}")
            os.remove('token.json')  # Remove invalid token file
            creds = None
    # If credentials are not valid, refresh or initiate the flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes=['https://www.googleapis.com/auth/calendar'])
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service


# Function to add task to Google Calendar
def add_task_to_calendar(service, email, task, date, start_time, end_time, reminder_days, priority):
    start_datetime = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    if task:
        user_input = task+','+str(date)+','+priority
        # Append user message to the conversation
        conversation.append({"role": "user", "content": user_input})
            # Check if the user is adding a task and add it to the tasks list
            # Use a maximum of the last 10 messages for context
        context_messages = conversation[-10:]
            # Send user message to OpenAI for a response
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=context_messages,
            temperature=0.7
        )
        reply = response.choices[0].message.content
            # Append assistant's reply to the conversation
        conversation.append({"role": "assistant", "content": reply})
            # Display the assistant's reply
        st.write(f"AI: You're task has been successfully created")
        print(reply)
        event = {
        'summary': reply,
        'description': f'Priority: {priority}',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'America/New_York',
        },
        'attendees': [{'email': email}],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': reminder_days * 24 * 60},  # Days before
                {'method': 'popup', 'minutes': 10},  # 10 minutes before
                {'method': 'popup', 'minutes': reminder_days * 24 * 60},
            ],
        },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
    #st.write(f'Task added to calendar: {event.get("htmlLink")}')
    else:
        main()

# Email sending function
def send_email(receiver_email, subject, body):
    sender_email = "aismarttask@gmail.com"  # Replace with your email
    sender_password = "yifu zgfl hcru lltp"  # Replace with your app-specific password

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error in sending email: {e}")

# Start of the Streamlit app
def main():
    st.title("AISmartTask Management System")

    # Streamlit app inputs
    email_input = st.text_input("Enter your email:")
    date_input = st.date_input("Select the date for the task:")
    start_time_input = st.time_input("Select the start time for the task:")
    end_time_input = st.time_input("Select the end time for the task:")
    reminder_days_input = st.number_input("Set a reminder (number of days before task):", min_value=0, value=1)
    priority_input = st.selectbox("Select task priority", ["High", "Medium", "Low"])
    task_input = st.text_input("Type your task here:")

    calendar_service = google_calendar_authenticate()

    if st.button("Add task"):
        add_task_to_calendar(calendar_service, email_input, task_input, date_input, start_time_input, end_time_input, reminder_days_input, priority_input)
        # Email content
        email_subject = "New Task Added"
        email_body = f"Task: {task_input}\nDate: {date_input}\nStart Time: {start_time_input}\nEnd Time: {end_time_input}\nReminder Days: {reminder_days_input}\nPriority: {priority_input}"
        send_email(email_input, email_subject, email_body)

    # ... [Rest of your app code]

if __name__ == "__main__":
    main()