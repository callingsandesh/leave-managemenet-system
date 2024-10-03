   -- Insert filtered results from source_table to destination_table
   MERGE INTO apidataupload_employee as employee
										USING
									(SELECT DISTINCT 
						"userId",
						"empId",
						"teamManagerId",
						"designationId",
						"firstName",
						"middleName",
						"lastName",
						"email",
						"isHr",
						"isSupervisor",
						"currentLeaveIssuerId",
						"currentLeaveIssuerEmail",
						"departmentDescription"
						FROM apidataupload_employeeleave el
    WHERE el."createdat_db" >=  %s 
									) a	
									ON employee."user_id" = a."userId"
									WHEN NOT MATCHED THEN
										INSERT (user_id,
										emp_id,
										team_manager_id,
										designation_id,
										first_name,
										middle_name,
										last_name,
										email,
										is_hr,
										is_supervisor,
										current_leave_issuer_id,
										current_leave_issuer_email,
										department_description)
										VALUES ("userId",
											"empId",
											"teamManagerId",
											"designationId",
											"firstName",
											"middleName",
											"lastName",
											"email",
											"isHr",
											"isSupervisor",
											"currentLeaveIssuerId",
											"currentLeaveIssuerEmail",
											"departmentDescription")
									 WHEN MATCHED THEN 
									 		UPDATE SET 
												team_manager_id=a."teamManagerId",
													designation_id=a."designationId",
													first_name=a."firstName",
													middle_name=a."middleName",
													last_name=a."lastName",
													email=a."email",
													is_hr=a."isHr",
													is_supervisor=a."isSupervisor",
													current_leave_issuer_id=a."currentLeaveIssuerId",
													current_leave_issuer_email=a."currentLeaveIssuerEmail",
													department_description=a."departmentDescription";

