import logging
from django.shortcuts import render
from asgiref.sync import async_to_sync
import time
import asyncio
import datetime
from urllib.parse import urlparse, parse_qs
import os
from dotenv import load_dotenv
from .forms import UploadFileForm
from django.http import HttpResponse
import pytz
from utils.utils_sql import read_sql_file
from apidataupload.service import call_stored_proc_async, chunk_data, save_chunk, fetch_data_for_interval, generate_date_intervals, handle_uploaded_file
from user.decorator import authenticated_user 

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

@authenticated_user
def navigation(request):
    logger.info(f"User {request.user} accessed navigation page.")
    if request.user.is_authenticated:
        return render(request, 'navigation.html', {'user': request.user})
    else:
        logger.warning("Unauthorized access attempt to navigation page.")
        return HttpResponse('Unauthorized', status=401)

@authenticated_user
def index(request):
    logger.info(f"User {request.user} accessed index page.")
    return render(request, 'index.html')

@authenticated_user
@async_to_sync
async def handle_api_data(request):
    if request.method == 'GET':
        logger.info("Handling API data request.")
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
        logger.info(f"Fetching data took: {end_time - start_time} seconds.")
        
        # Combine all the data
        data = []
        for result in results:
            if 'data' in result:
                data.extend(result['data'])
            else:
                logger.error(f"Error fetching data: {result}")

        createdat_db = datetime.datetime.today()
        timezone = pytz.timezone('Asia/Kathmandu')  # Set your desired timezone here
        aware_datetime = timezone.localize(createdat_db)
        # Define chunk size
        chunk_size = int(os.getenv('CHUNK_SIZE'))
        start_time = time.time()
        chunks = chunk_data(data, chunk_size)
        tasks = [save_chunk(chunk, aware_datetime) for chunk in chunks]
        await asyncio.gather(*tasks)
        end_time = time.time()
        logger.info(f"Saving data took: {end_time - start_time} seconds.")
        
        # Normalize data in raw table 
        SQL_FILE_PATHS = os.getenv('SQL_FILE_PATHS')      
        file_paths_list = SQL_FILE_PATHS.split(',')  # Convert the string into a list by splitting it by commas     
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        sql_scripts = []
        for file_name in file_paths_list:
            file_name = file_name.strip()
            sql_file_path = os.path.join(BASE_DIR, 'sql', file_name)
            if os.path.exists(sql_file_path):
                sql_scripts.append(sql_file_path)
            else:
                logger.error(f"SQL file not found: {file_name}")
                return HttpResponse(f"SQL file not found: {file_name}", status=404)  
        
        sql_queries = [read_sql_file(file_path) for file_path in sql_scripts]
        tasks = [call_stored_proc_async(sql_query, aware_datetime) for sql_query in sql_queries]
        await asyncio.gather(*tasks)  # Run all tasks concurrently
        logger.info("Employee leave records have been successfully saved.")
        return HttpResponse("Employee leave records have been successfully saved.")
    
    logger.warning("No POST request received for API data.")
    return HttpResponse('No post request')

@authenticated_user
@async_to_sync
async def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            chunk_size = 30000  
            start_time = time.time()
            chunks = chunk_data(data, chunk_size)
            createdat_db = datetime.datetime.today()
            timezone = pytz.timezone('Asia/Kathmandu')  # Set your desired timezone here
            aware_datetime = timezone.localize(createdat_db)
            logger.info(f"Uploading file: {file.name} at {aware_datetime}.")
            tasks = [save_chunk(chunk, aware_datetime) for chunk in chunks]
            await asyncio.gather(*tasks)
            end_time = time.time()
            logger.info(f"Saving data took: {end_time - start_time} seconds.")
            
            SQL_FILE_PATHS = os.getenv('SQL_FILE_PATHS') 
            file_paths_list = SQL_FILE_PATHS.split(',')  # Convert the string into a list by splitting it by commas
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logger.info(f"Base directory for SQL files: {BASE_DIR}.")
            
            sql_scripts = []
            for file_name in file_paths_list:
                file_name = file_name.strip()
                sql_file_path = os.path.join(BASE_DIR, 'sql', file_name)
                if os.path.exists(sql_file_path):
                    sql_scripts.append(sql_file_path)
                else:
                    logger.error(f"SQL file not found: {file_name}")
                    return HttpResponse(f"SQL file not found: {file_name}", status=404)  
            
            sql_queries = [read_sql_file(file_path) for file_path in sql_scripts]
            tasks = [call_stored_proc_async(sql_query, aware_datetime) for sql_query in sql_queries]  
            await asyncio.gather(*tasks)  # Run all tasks concurrently
            logger.info("File has been uploaded and data saved successfully.")
            return HttpResponse("File has been uploaded and data saved successfully.")
    
    logger.warning("Invalid form submission or method not POST.")
    form = UploadFileForm()  # Reset the form for GET request
    return render(request, 'upload.html', {'form': form})
