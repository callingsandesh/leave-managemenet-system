from django.db import connection,DatabaseError
from django.http import HttpResponse
from asgiref.sync import sync_to_async
from .models import EmployeeLeave
import pandas as pd
import numpy as np
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import datetime

def call_stored_proc_to_normalize_data(procedurename,filter_datetime):
    with connection.cursor() as cursor:
        cursor.callproc(procedurename, [filter_datetime]) # Add your procedure name and parameters here
        results = cursor.fetchall()  # Fetch results if your procedure returns any

    # Process results as needed and return an appropriate HTTP response
    return results

async def call_stored_proc_async(sql_query, createdat_filter):
    return await sync_to_async(call_stored_proc_sync)(sql_query, createdat_filter)

def call_stored_proc_sync(sql_query, createdat_filter):
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query,[createdat_filter])              
            print("Executed")
    except DatabaseError as e:
        print(f"Database error: {str(e)}")
        return HttpResponse(f"SQL file could not be executed: {sql_query}. Error: {str(e)} .Query: {cursor.mogrify(sql_query, [createdat_filter]).decode('utf-8')}", status=500) 
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return HttpResponse(f"An unexpected error occurred while executing: {sql_query}. Error: {str(e)}", status=500)
    
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