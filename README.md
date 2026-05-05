# application_copilot
Copilot to help with job applications

1. Configuration

Within application_copilot folder, create config.py

Add the following into your file:

SEARCH_QUERY = "" # enter what job you wish to look for

LOCATION = "" # enter where you wish to be located, remote will always be included no matter where you put

MAX_PAGES = 3  # keep low to avoid detection



2. Ingestion

After you have configured the settings to search for jobs you want, all you need to do is input the command:

python -m ingestion.main

You must be in the application_copilot directory when you execute the command.



3. Frontend

Input the command from the application_copilot directory:

univorn app.main:app --reload

Next, open your browser and input the following URL:

127.0.0.1:8000
