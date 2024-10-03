from django.db import connection
from django.shortcuts import render , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apidataupload.models import Employee , Leave 
from datetime import datetime, timedelta

@login_required
def employee_count_by_designation_view(request):
    return render(request, 'visualizations/employee_count_by_designation.html')

def employee_count_by_designation(request):
    department = request.GET.get('department')
    if department == 'all':
        query = """SELECT d.name, COUNT(e.id) 
                FROM apidataupload_employee e 
                JOIN apidataupload_designation d ON e.designation_id = d.id 
                GROUP BY d.name"""
        params = []
    else:
        query="""SELECT d.name, COUNT(e.id) 
                FROM apidataupload_employee e 
                JOIN apidataupload_designation d ON e.designation_id = d.id
                WHERE e.department_description = %s 
                GROUP BY d.name"""
        params=[department]
        
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    data = [{'designation': row[0], 'count': row[1]} for row in rows]
    return JsonResponse(data, safe=False)

def leave_type_distribution(request):
    query = """SELECT lt.leave_type , count(l.id)  FROM apidataupload_leave l
				JOIN apidataupload_leavetype lt ON l.leave_type_id = lt.id
				GROUP BY lt.leave_type"""     
        
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    data = [{'label': row[0], 'count': row[1]} for row in rows]
    return JsonResponse(data, safe=False)

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'visualizations/employee_list.html', {'employees': employees})

@login_required
def employee_detail(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    leaves = Leave.objects.filter(employee=employee)
    return render(request, 'visualizations/employee_detail.html', {'employee': employee, 'leaves': leaves})

@login_required
def employee_leave_trend(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = (datetime.now() - timedelta(weeks=2)).date()
    if not end_date:
        end_date = datetime.now().date()

    query = """
        SELECT
            DATE_TRUNC('day', "start_date")::DATE AS Day,
            COUNT(*) AS leave_count
        FROM
            "apidataupload_leave"
        WHERE
            "start_date" BETWEEN %s AND %s
        GROUP BY
            DATE_TRUNC('day', "start_date")
        ORDER BY
            day;
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date, end_date])
        rows = cursor.fetchall()

    data = [{'label': row[0], 'count': row[1]} for row in rows]
    return JsonResponse(data, safe=False)

@login_required
def d3_visualization(request):
    return render(request, 'visualizations/d3_visualization.html')

@login_required
def leave_heatmap_api(request):
    start_date = request.GET.get('start_date', '2023-01-01')
    end_date = request.GET.get('end_date', '2024-12-31')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                "startDate"::DATE AS date,
                COUNT(*) AS leave_count
            FROM
                "apidataupload_employeeleave"
            WHERE
                "startDate"::DATE >= %s
                AND "startDate"::DATE <= %s
            GROUP BY
                "startDate"::DATE
            ORDER BY
                date;
        """, [start_date, end_date])
        heatmap_data = cursor.fetchall()

    # Prepare the data for JSON response
    data = [
        {
            'date': row[0].strftime('%Y-%m-%d'),
            'leave_count': row[1]
        }
        for row in heatmap_data
    ]
    return JsonResponse(data, safe=False)