from django.shortcuts import render
import requests
from django.http import HttpResponse
from asgiref.sync import sync_to_async
from asgiref.sync import async_to_sync
from .models import EmployeeLeave
import time
import asyncio
import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import os
from dotenv import load_dotenv
import pandas as pd
from .forms import UploadFileForm
import numpy as np
#from rest_framework.decorators import api_view, permission_classes
#from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.db import connection
import pytz
from utils.utils_sql import read_sql_file
from leavemgt.settings import BASE_DIR
# Load environment variables from .env file
load_dotenv()

@login_required
def navigation(request):
    return render(request, 'navigation.html')


@login_required
def index(request):
    return render(request, 'index.html')


def chunk_data(data, chunk_size):
    """Split data into chunks of specified size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

async def save_chunk(chunk,createdat_db):
    """Save a chunk of data to the database asynchronously."""
    instances = [create_employee_leave_instance(item,createdat_db) for item in chunk]
    await sync_to_async(EmployeeLeave.objects.bulk_create)(instances)


async def fetch_data_for_interval(base_url, headers, interval_start, interval_end):
    """Fetch data for a specific date interval."""
    url_parts = list(urlparse(base_url))
    query = parse_qs(url_parts[4])
    query['startDate'] = interval_start
    query['endDate'] = interval_end
    url_parts[4] = urlencode(query, doseq=True)
    interval_url = urlunparse(url_parts)
    print(interval_url)
    response = await sync_to_async(requests.get)(interval_url, headers=headers)
    return response.json()

def generate_date_intervals(start_date, end_date):
    """Generate three-month date intervals between start_date and end_date."""
    intervals = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + datetime.timedelta(days=180), end_date)
        intervals.append((current_start, current_end))
        current_start = current_end + datetime.timedelta(days=1)
    return intervals

def handle_uploaded_file(file):
    # Determine file type and parse accordingly
    if file.name.endswith('.csv'):
        data = pd.read_csv(file)
    elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
        data = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type")

    # Convert DataFrame to list of dictionaries
    data = data.to_dict(orient='records')
    return data



def handle_uploaded_file(file):
    # Determine file type and parse accordingly
    if file.name.endswith('.csv'):
        data = pd.read_csv(file)
    elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
        data = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type")

    # Replace NaN values with appropriate defaults
    data = data.replace({np.nan: None})
    
    # Convert DataFrame to list of dictionaries
    data = data.to_dict(orient='records')
    return data

def call_stored_proc_to_normalize_data(procedurename,filter_datetime):
    with connection.cursor() as cursor:
        cursor.callproc(procedurename, [filter_datetime]) # Add your procedure name and parameters here
        results = cursor.fetchall()  # Fetch results if your procedure returns any

    # Process results as needed and return an appropriate HTTP response
    return results


async def call_stored_proc_async(sql_query, createdat_filter):
    return await sync_to_async(call_stored_proc_sync)(sql_query, createdat_filter)

def call_stored_proc_sync(sql_query, createdat_filter):
    with connection.cursor() as cursor:
        cursor.execute(sql_query,[createdat_filter])              
        print("Executed")
    pass




#@api_view(['GET', 'POST'])
#@permission_classes([IsAuthenticated])
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
        chunk_size = 30000  # Adjust this size based on your needs and database capacity

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
        base_url = os.getenv('BASE_URL')    
        sql_queries=[read_sql_file(base_url+file_path) for file_path in file_paths_list]
        tasks = [call_stored_proc_async(sql_query, aware_datetime) for sql_query in sql_queries]
            
        await asyncio.gather(*tasks) # Run all tasks concurrently
        return HttpResponse("Employee leave records have been successfully saved.")
    return HttpResponse('No post request')

# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
@async_to_sync
@login_required
async def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            data = handle_uploaded_file(file)
            # Define chunk size
            chunk_size = 30000  # Adjust this size based on your needs and database capacity

            start_time = time.time()
            chunks = chunk_data(data, chunk_size)
            createdat_db=datetime.datetime.today()
            timezone = pytz.timezone('Asia/Kathmandu')  # Set your desired timezone here
            aware_datetime = timezone.localize(createdat_db)
            tasks = [save_chunk(chunk,aware_datetime) for chunk in chunks]
            await asyncio.gather(*tasks)
            end_time = time.time()
            print(f"Saving data took: {end_time - start_time} seconds")
            
            SQL_FILE_PATHS = os.getenv('SQL_FILE_PATHS')
            
            file_paths_list = SQL_FILE_PATHS.split(',') # Convert the string into a list by splitting it by commas
            
            base_url = os.getenv('BASE_URL')
            
            sql_queries=[read_sql_file(base_url+file_path) for file_path in file_paths_list]
            tasks = [call_stored_proc_async(sql_query, aware_datetime) for sql_query in sql_queries]
            
            await asyncio.gather(*tasks) # Run all tasks concurrently
            return HttpResponse("File has been uploaded and data saved successfully.")
    else:
        try:
            form = UploadFileForm()
        except:
            pass 
    return render(request, 'upload.html', {'form': form})


def create_employee_leave_instance(item,createdat_db):
    return EmployeeLeave(
        id_s=item['id'],
        userId=item['userId'],
        empId=item['empId'],
        teamManagerId=item['teamManagerId'],
        designationId=item['designationId'],
        designationName=item['designationName'],
        firstName=item['firstName'],
        middleName=item.get('middleName'),
        lastName=item['lastName'],
        email=item['email'],
        isHr=item['isHr'],
        isSupervisor=item['isSupervisor'],
        leaveIssuerId=item['leaveIssuerId'],
        currentLeaveIssuerId=item['currentLeaveIssuerId'],
        issuerFirstName=item['issuerFirstName'],
        issuerMiddleName=item.get('issuerMiddleName'),
        issuerLastName=item['issuerLastName'],
        currentLeaveIssuerEmail=item['currentLeaveIssuerEmail'],
        departmentDescription=item['departmentDescription'],
        startDate=item['startDate'],
        endDate=item['endDate'],
        leaveDays=item['leaveDays'],
        reason=item['reason'],
        leaveStatus=item['leaveStatus'],
        status=item['status'],
        responseRemarks=item.get('responseRemarks'),
        leaveTypeId=item['leaveTypeId'],
        leaveType=item['leaveType'],
        defaultDays=item['defaultDays'],
        transferableDays=item['transferableDays'],
        isConsecutive=item['isConsecutive'],
        fiscalId=item['fiscalId'],
        fiscalStartDate=item['fiscalStartDate'],
        fiscalEndDate=item['fiscalEndDate'],
        fiscalIsCurrent=item['fiscalIsCurrent'],
        createdAt=item['createdAt'],
        updatedAt=item['updatedAt'],
        isAutomated=item['isAutomated'],
        isConverted=item['isConverted'],
        allocations=item.get('allocations'),
        createdat_db=createdat_db
    )
