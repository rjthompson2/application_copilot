# application_copilot
Copilot to help with job applications

1. Configuration

2. Ingestion
After you have configured the settings to search for jobs you want, all you need to do is input the command:
python -m ingestion.main

You must be in the application_copilot directory when you execute the command.

3. Frontend
Input the command from the application_copilot directory:
univorn app.main:app --reload

Next, open your browser and input the following URL:
127.0.0.1:8000
