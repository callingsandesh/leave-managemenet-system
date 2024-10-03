from django.shortcuts import render
from asgiref.sync import async_to_sync
import time
import asyncio
import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os
from dotenv import load_dotenv
from .forms import UploadFileForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import pytz
from utils.utils_sql import read_sql_file
from apidataupload.service import call_stored_proc_async,create_employee_leave_instance,chunk_data,save_chunk,fetch_data_for_interval,generate_date_intervals,handle_uploaded_file

# Load environment variables from .env file
load_dotenv()

@login_required
def navigation(request):
    return render(request, 'navigation.html')

@login_required
def index(request):
    return render(request, 'index.html')

@async_to_sync
@login_required
async def handle_api_data(request):
    if request.method == 'GET':
        url = os.getenv('API_URL')
        headers = {
            'Authorization': os.getenv('API_AUTHORIZATION')
        }
        # Extract startDate and endDate from the URL
        url_parts = list(urlparse(url))
        query = parse_qs(url_parts[4])
        start_date = datetime.datetime.strptime(query['startDate'][0], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(query['endDate'][0], '%Y-%m-%d').date()

        # Generate date intervals
        intervals = generate_date_intervals(start_date, end_date)
        
        start_time = time.time()
        # Fetch data asynchronously for all intervals
        tasks = [fetch_data_for_interval(url, headers, interval[0].isoformat(), interval[1].isoformat()) for interval in intervals]
        results = await asyncio.gather(*tasks)  
        end_time = time.time()
        print(f"Fetching data took: {end_time - start_time} seconds")
        # Combine all the data
        data = []
        for result in results:
            if 'data' in result:
                data.extend(result['data'])
            else:
                print(f"Error fetching data: {result}")
        print(f"Fetching data took: {end_time - start_time} seconds")
        createdat_db=datetime.datetime.today()
        timezone = pytz.timezone('Asia/Kathmandu')  # Set your desired timezone here
        aware_datetime = timezone.localize(createdat_db)
        # Define chunk size
        chunk_size = int(os.getenv('CHUNK_SIZE'))
        start_time = time.time()
        #createdat_db=datetime.datetime.today()
        chunks = chunk_data(data, chunk_size)
        tasks = [save_chunk(chunk,aware_datetime) for chunk in chunks]
        await asyncio.gather(*tasks)
        end_time = time.time()
        print(f"Saving data took: {end_time - start_time} seconds")
        #code to normalize data in raw table 
        SQL_FILE_PATHS = os.getenv('SQL_FILE_PATHS')      
        file_paths_list = SQL_FILE_PATHS.split(',') # Convert the string into a list by splitting it by commas     
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Initialize an empty list to hold SQL script contents
        sql_scripts = []
        # Construct full paths and read each SQL file
        for file_name in file_paths_list:
            file_name =  file_name.strip()
            sql_file_path = os.path.join(BASE_DIR, 'sql', file_name)
            if os.path.exists(sql_file_path):
                sql_scripts.append(sql_file_path)
            else:
                return HttpResponse(f"SQL file not found: {file_name}", status=404)  
        sql_queries=[read_sql_file(file_path) for file_path in sql_scripts]
        tasks = [call_stored_proc_async(sql_query, aware_datetime) for sql_query in sql_queries]
            
        await asyncio.gather(*tasks) # Run all tasks concurrently
        return HttpResponse("Employee leave records have been successfully saved.")
    return HttpResponse('No post request')

@login_required
@async_to_sync
async def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            # Define chunk size
            chunk_size = 30000  

            start_time = time.time()
            chunks = chunk_data(data, chunk_size)
            createdat_db=datetime.datetime.today()
            timezone = pytz.timezone('Asia/Kathmandu')  # Set your desired timezone here
            aware_datetime = timezone.localize(createdat_db)
            print(aware_datetime)
            tasks = [save_chunk(chunk,aware_datetime) for chunk in chunks]
            await asyncio.gather(*tasks)
            end_time = time.time()
            print(f"Saving data took: {end_time - start_time} seconds")
            SQL_FILE_PATHS = os.getenv('SQL_FILE_PATHS') 
            file_paths_list = SQL_FILE_PATHS.split(',') # Convert the string into a list by splitting it by commas
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print(BASE_DIR)
            # Initialize an empty list to hold SQL script contents
            sql_scripts = []
            # Construct full paths and read each SQL file
            for file_name in file_paths_list:
                file_name =  file_name.strip()
                sql_file_path = os.path.join(BASE_DIR, 'sql', file_name)
                if os.path.exists(sql_file_path):
                    sql_scripts.append(sql_file_path)
                else:
                    return HttpResponse(f"SQL file not found: {file_name}", status=404)  
            sql_queries=[read_sql_file(file_path) for file_path in sql_scripts]
            tasks = [call_stored_proc_async(sql_query, aware_datetime) for sql_query in sql_queries]  
            await asyncio.gather(*tasks) # Run all tasks concurrently
            return HttpResponse("File has been uploaded and data saved successfully.")
    else:
        try:
            form = UploadFileForm()
        except:
            pass 
    return render(request, 'upload.html', {'form': form})


