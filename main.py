from __future__ import print_function
import pickle
import os
import os.path
import mysql.connector
import datetime
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from ast import literal_eval
from dotenv import load_dotenv

load_dotenv()


# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "google_credentials.json", SCOPES)
            creds = flow.run_local_server()
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

    service = build("sheets", "v4", credentials=creds)
    return service


def getData():
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PWD = os.getenv('MYSQL_PWD')
    MYSQL_SCHEMA = os.getenv('MYSQL_SCHEMA')
    DB_QUERY = os.getenv('DB_QUERY')
    sh_db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PWD,
        database=MYSQL_SCHEMA
        #ssl_disabled = "True"
    )

    db_cursor = sh_db.cursor()

    #execute query
    db_cursor.execute(DB_QUERY)

    # Enter your column names as 2-d list
    # These names will be saved as column titles in your Google Sheet
    headers = [i.strip() for i in os.getenv('DATA_HEADER').split(",")]
    data = [
        headers
    ]

    result = db_cursor.fetchall()
    data += result
    return data

def clear_data(sheet_service):

    # Enter the ID of the Google Spreadsheet in which we are going to save the data
    # Make sure that the authenticated account has access to this Google Sheet
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    DATA_RANGE = os.getenv('DATA_RANGE')
    values = {'ranges':[DATA_RANGE]}

    #clear the sheet
    start_time = time.time()
    print("Clearing data for range [ %s ]" % DATA_RANGE)
    response = sheet_service.spreadsheets( ).values( ).batchClear( spreadsheetId=SPREADSHEET_ID,body=values).execute()
    print("Clearing data completed in %s seconds" % round((time.time() - start_time),2))
    return response

def write_data(sheet_service,data):
    # Enter the ID of the Google Spreadsheet in which we are going to save the data
    # Make sure that the authenticated account has access to this Google Sheet
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    DATA_RANGE = os.getenv('DATA_RANGE')
    values = {"majorDimension": "ROWS", "values": data}

    # Data will be updated in RAW format. 
    # Any additional formatting if needed, will have to done manually post update. ex: converting a column to Currency
    request = (
        sheet_service.spreadsheets()
        .values()
        .update(
            spreadsheetId=SPREADSHEET_ID,
            range=DATA_RANGE,
            body=values,
            valueInputOption="RAW",
        )
    )
    print("Updating data for range [ %s ]" % DATA_RANGE)
    start_time = time.time()
    response = request.execute()
    print("Updating data completed in %s seconds" % round((time.time() - start_time),2))
    return response



def main():

    #AUTH
    print("Authenticating...")
    SERVICE = authenticate()
    print("Done!!!")

    #DB
    start_time = time.time()
    print("Querying data started")
    DATA = getData()
    print("Querying data completed in %s seconds" % round((time.time() - start_time),2))

    #GSHEET 
    clear_data(SERVICE)
    write_data(SERVICE,DATA)


if __name__ == "__main__":
    main()
