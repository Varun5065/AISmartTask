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
from datetime import datetime, time
import autogen
from dateutil import parser
from datetime import datetime
import re

# Set up your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
# model architectur for task creation
task_conversation = []
task_list = []
system_message = {
    "role": "system",
    "content": """You are AISmartTask: An innovative AI-driven task management solution tailored for coders or anyone who likes to manage daily routines. You offer an intuitive user experience. Key features include dynamic task management that allows for task addition, prioritization, and AI-powered task suggestions. You can accept documents in the form of text, and your document parser extracts essential summaries and highlights critical keywords from that document. Additionally, AISmartTask visualizes task priorities, enabling users to get a clearer view of their tasks at hand. Your one standout quality is your learning modules, which web scrape for knowledge, encouraging continuous learning. Users can interact with you and provide feedback for continuous system improvement. AISmartTask is not just a task manager; it's a revolutionary tool aiming to optimize and enhance the daily routines of coders. It is scalable to any user and other applications such as enterprise project management, academic tasks management (students and educators), task management in healthcare, and in the freelance and gig economy.
    Create a plan for user on how they can deivide the task and can complete it by the deadline."""
}
task_conversation.append(system_message)
priority = 'medium'
remainder_days = 1

#coder uisng Microsoft's AutoGPT framework
def code(user_input):
    config_list=[{
    'model': 'gpt-4',
    'api_key': openai_api_key
    }]
    general_llm_config={
    'request_timeout':600,
    'seed':42,
    'config_list':config_list,
    'temperature':0
    }
    assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={
        "cache_seed": 42,  # seed for caching and reproducibility
        "config_list": config_list,  # a list of OpenAI API configurations
        "temperature": 0,  # temperature for sampling
    },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )
# create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False
    },
    )
# the assistant receives a message from the user_proxy, which contains the task description
    user_proxy.initiate_chat(
    assistant,
    message=user_input,
    clear_history=False
    )
    first_key = next(iter(user_proxy.chat_messages))
    values_of_first_key = user_proxy.chat_messages[first_key]
    reply = values_of_first_key[-3]['content']
    st.write(reply)
    

def google_calendar_authenticate(): # authentication
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



def add_task_to_calendar(service, email, tasks):
    for i in tasks:
        # for each task in the format of [a,b,c , c,b,a]
        task, date_str, priority = i.split(',')
        # converting the user enterd date into iso format
        # Remove ordinal suffixes
        date_str = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date_str)
        # Add a space between month and day if missing
        date_str = re.sub(r'([A-Za-z]+)(\d)', r'\1 \2', date_str)
        # Convert two-digit year to four-digit year (assuming 2000s)
        if re.search(r'\b\d{2}\b', date_str) and not re.search(r'\b\d{4}\b', date_str):
            two_digit_year = re.search(r'\b\d{2}\b', date_str).group()
            four_digit_year = '20' + two_digit_year
            date_str = re.sub(r'\b\d{2}\b', four_digit_year, date_str)
        elif not re.search(r'\b\d{2}\b', date_str) and not re.search(r'\b\d{4}\b', date_str):
            current_year = datetime.now().year
            date_str += f' {current_year}'
        # Parse the date
        date_obj = parser.parse(date_str)
        # Convert to ISO 8601 format
        iso_date = date_obj.date().isoformat()
        task_list.append({'task':task, 'deadline':iso_date, 'priority':priority}) # task list of the user
        # adding events to the calender
        event = {
            'summary': task,
            'description': f'Priority: {priority}',
            'start': {
                'date': iso_date,
                'timeZone': 'America/New_York'
            },
            'end': {
                'date': iso_date,  # You may want to adjust this based on the event duration
                'timeZone': 'America/New_York'
            },
            'attendees': [{'email': email}],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': remainder_days * 24 * 60},  # Days before
                    {'method': 'popup', 'minutes': 10},  # 10 minutes before
                    {'method': 'popup', 'minutes': remainder_days * 24 * 60},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()

# Function to create the plan for the user
def create_plan(calender_service, email, task_input):
    tasks = task_input.split('|') # splititng the tasks
    st.write('Creating')
    inp = 'Give me a detailed day to day plan for my following tasks:'+ task_input # prompt used for creating the plan
    task_conversation.append({"role": "user", "content": inp})
    response = openai.chat.completions.create(
            model="gpt-4",
            messages=task_conversation,
            temperature=0.7
    )
    reply = response.choices[0].message.content
    st.write('Done')
    # Append assistant's reply to the conversation
    task_conversation.append({"role": "assistant", "content": reply})
    # Display the assistant's reply
    st.write(f"AI: You're task has been successfully created")
    send_email(email, 'Tasks-To-Do', reply) # email
    add_task_to_calendar(calender_service, email, tasks) # adding the events to calender
    st.write(reply)
    return 

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

def manage_tasks():
    calendar_service = google_calendar_authenticate() # authentication for access.
    st.subheader("How to Use This Application") # isntructions for input
    st.markdown("""
    * **Step 1**: Enter your task details in the provided text area. 
    * **Step 2**: Click on 'Manage Task' to add the task to your calendar and send an email notification.
    * **Step 3**: By default, the pripority is set to medium and the remainder_days is set to 1 day before.
    * **Step 4**: If you need to use the code agent, input the necessary information and click the respective button.
    * **Step 5**: If you have multiple tasks, please use the '|' symbol to divide your tasks.
    * **Step 6**: Date format:('Nov25th 23' or 'Nov 25th'(for this current year is considered) or 'Nov 25th 2023').
    """)
    task_input = st.text_area("Enter task details (Format: task, date, priority):")
    email= st.text_input("Enter your email:") # email for sending the created plan
    if st.button("Create Task Plan"):
        create_plan(calendar_service, email, task_input) # to create the plan using gpt-4
        # Filtering and sorting tasks and showing the tasks ina tabular format
        current_date = datetime.now().date()
        updated_tasks = [task for task in task_list if datetime.fromisoformat(task["deadline"]).date() >= current_date]
        pending_tasks = sorted(updated_tasks, key=lambda x: datetime.fromisoformat(x["deadline"]).date())
        st.write("Upcoming Tasks:")
        st.table(pending_tasks)
        st.session_state.task_plan_active = True
        
def coder():
    st.subheader("Code Agent")
    code_input = st.text_area("Enter code-related query:")
    # Trigger the code function without resetting the session state
    if st.button("Get Code Help"):
        code(code_input)

# Start of the Streamlit app
def main():
    st.header("Welcome to AISmartTask Management System")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Manage Task"):
            st.session_state.manage_tasks = True
            st.session_state.task_plan_active = True
            st.session_state.code_active = False
    with col2:
        if st.button("Code Agent"):
            st.session_state.code_active = True
            st.session_state.manage_tasks = False
            st.session_state.task_plan_active = False

    if st.session_state.get('manage_tasks', False) and st.session_state.get('task_plan_active', False):
        manage_tasks()
    if st.session_state.get('code_active', False):
        coder()

# Initialize the session state variables
if 'manage_tasks' not in st.session_state:
    st.session_state.manage_tasks = False

if 'task_plan_active' not in st.session_state:
    st.session_state.task_plan_active = False

if 'code_active' not in st.session_state:
    st.session_state.code_active = False

if __name__ == "__main__":
    main()
