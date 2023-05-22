from __future__ import print_function
import datetime
import os.path
import sqlite3
from sys import argv

import pytz

import streamlit as st
from dateutil import parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# ADD YOUR CALENDAR ID HERE
YOUR_CALENDAR_ID = 'Add Your Calendar ID Here'
YOUR_TIMEZONE = 'America/New_York'  # find yours here: https://www.timezoneconverter.com/cgi-bin/zonehelp.tzc?cc=US&ccdesc=United%20States


# Authenticate with Google Calendar
def authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds



# Add calendar event with random time on the given date for the specified duration
def add_event(creds, duration, description, task_date):
    # Generate a random time within the day
    start_time = datetime.datetime.combine(task_date, datetime.time.min)
    end_time = start_time + datetime.timedelta(minutes=int(duration))

    eastern_tz = pytz.timezone('America/New_York')
    start_formatted = start_time.astimezone(eastern_tz).isoformat()
    end_formatted = end_time.astimezone(eastern_tz).isoformat() 

    event = {
        'summary': description,
        'start': {
            'dateTime': start_formatted,
            'timeZone': 'America/New_York',
        },
        'end': {
            'dateTime': end_formatted,
            'timeZone': 'America/New_York',
        },
    }

    service = build('calendar', 'v3', credentials=creds)
    event = service.events().insert(calendarId=YOUR_CALENDAR_ID, body=event).execute()
    st.write('Event created: %s' % (event.get('htmlLink')))





def main():
    
    st.title("Time Management System")
    st.write("Welcome to the Time Management System! This app will help you add task to your google calendar.")

    creds = authenticate()
    task_duration = st.slider("Task duration (in minutes):", min_value=0, max_value=180, value=60)
    

    description = st.text_input("Description")
    task_date = st.date_input("Task date")
    if st.button("Add"):
            add_event(creds, task_duration, description, task_date)
            st.success("Event added successfully!")






if __name__ == '__main__':
    main()
