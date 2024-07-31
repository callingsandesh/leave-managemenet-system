from django.db import models


class Designation(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class LeaveType(models.Model):
    id = models.IntegerField(primary_key=True)
    leave_type = models.CharField(max_length=100)

    def __str__(self):
        return self.leave_type


class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    emp_id = models.CharField(max_length=20, blank=True,unique=True,null=True)
    team_manager_id = models.IntegerField(blank=True,default=None,null=True)
    first_name = models.CharField(max_length=100, blank=True,null=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, blank=True,null=True)
    email = models.EmailField(unique=True, blank=True,null=True)
    is_hr = models.BooleanField(blank=True,null=True)
    is_supervisor = models.BooleanField(blank=True,null=True)
    current_leave_issuer_id = models.IntegerField(default=None,null=True,blank=True)
    current_leave_issuer_email = models.EmailField(default='unknown@unknown.com',null=True, blank=True)  # Provide a default value here
    department_description = models.TextField(default=None)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Leave(models.Model):
    id = models.IntegerField(primary_key=True)
    employee = models.ForeignKey(Employee,to_field='emp_id', on_delete=models.CASCADE)
    leave_type= models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_days = models.IntegerField()
    reason = models.TextField(blank=True,null=True)
    leave_status = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    response_remarks = models.TextField(null=True, blank=True)
    default_days = models.IntegerField(null=True)
    transferable_days = models.IntegerField()
    is_consecutive = models.BooleanField(blank=True,null=True)
    fiscal_id = models.IntegerField()
    fiscal_start_date = models.DateField()
    fiscal_end_date = models.DateField()
    fiscal_is_current = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(null=True,blank=True)
    is_automated = models.BooleanField(blank=True,null=True)
    is_converted = models.BooleanField(blank=True,null=True)
    leave_issuer_id = models.IntegerField(blank=True,null=True)
    issuer_first_name = models.CharField(max_length=100,blank=True,null=True)
    issuer_middle_name = models.CharField(max_length=100, null=True, blank=True)
    issuer_last_name = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return f'{self.leave_type} ({self.start_date} to {self.end_date})'
    

class EmployeeLeave(models.Model):
    id_s = models.IntegerField(null=True)
    userId = models.IntegerField(null=True)
    empId = models.CharField(max_length=10, null=True)
    teamManagerId = models.IntegerField(null=True)
    designationId = models.IntegerField(null=True)
    designationName = models.CharField(max_length=100, null=True)
    firstName = models.CharField(max_length=100, null=True)
    middleName = models.CharField(max_length=100, null=True)
    lastName = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    isHr = models.BooleanField(null=True)
    isSupervisor = models.BooleanField(null=True)
    leaveIssuerId = models.IntegerField(null=True)
    currentLeaveIssuerId = models.IntegerField(null=True)
    issuerFirstName = models.CharField(max_length=100, null=True)
    issuerMiddleName = models.CharField(max_length=100, null=True)
    issuerLastName = models.CharField(max_length=100, null=True)
    currentLeaveIssuerEmail = models.EmailField(null=True)
    departmentDescription = models.TextField(null=True)
    startDate = models.DateField(null=True)
    endDate = models.DateField(null=True)
    leaveDays = models.IntegerField(null=True)
    reason = models.TextField(null=True)
    leaveStatus = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=20, null=True)
    responseRemarks = models.TextField(null=True)
    leaveTypeId = models.IntegerField(null=True)
    leaveType = models.CharField(max_length=50, null=True)
    defaultDays = models.IntegerField(null=True)
    transferableDays = models.IntegerField(null=True)
    isConsecutive = models.BooleanField(null=True)
    fiscalId = models.IntegerField(null=True)
    fiscalStartDate = models.DateTimeField(null=True)
    fiscalEndDate = models.DateTimeField(null=True)
    fiscalIsCurrent = models.BooleanField(null=True)
    createdAt = models.DateTimeField(null=True)
    updatedAt = models.DateTimeField(null=True)
    isAutomated = models.BooleanField(null=True)
    isConverted = models.BooleanField(null=True)
    allocations = models.TextField(null=True)
    createdat_db = models.DateTimeField(null=True)
    def __str__(self):
        return f"{self.firstName} {self.lastName} - {self.leaveType}"

