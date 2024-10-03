-- Insert filtered results from source_table to destination_table
merge INTO apidataupload_leavetype AS lt
USING (SELECT DISTINCT "leaveTypeId",
                       "leaveType"
       FROM   apidataupload_employeeleave el
       WHERE  el."createdat_db" >=%s) a
ON lt."id" = a."leaveTypeId"
WHEN NOT matched THEN
  INSERT ( "id",
           "leave_type" )
  VALUES ( "leaveTypeId",
           "leaveType" )
WHEN matched THEN
  UPDATE SET "id" = a."leaveTypeId",
             "leave_type" = a."leaveType"; 