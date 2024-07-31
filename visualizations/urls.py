from django.urls import path
from .views import  employee_count_by_designation_view,employee_count_by_designation,leave_type_distribution,employee_list,employee_detail,employee_leave_trend,leave_heatmap_api,d3_visualization

urlpatterns = [
    path('employee-count-by-designation/', employee_count_by_designation, name='employee_count_by_designation'),
    path('employee-count-by-designation-view/', employee_count_by_designation_view, name='employee-count-by-designation-view'),
    path('leave_type_distribution/', leave_type_distribution, name='leave_type_distribution'),
    path('employees/', employee_list, name='employee_list'),
    path('employees/<int:employee_id>/', employee_detail, name='employee_detail'),
    path('employee_leave_trend/', employee_leave_trend, name='emplyee_leave_trend'),
    path('d3_visualization/',d3_visualization,name='d3_visualization'),
    path('leave-heatmap/', leave_heatmap_api, name='leave_heatmap_api'),
]
