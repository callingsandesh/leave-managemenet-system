# Import module

def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    

file_paths_list=['leavemgt/sql/filter_and_insert_into_designation.sql', 'leavemgt/sql/filter_and_insert_into_leavetype.sql', 'leavemgt/sql/filter_and_insert_into_employee.sql', 'leavemgt/sql/filter_and_insert_into_leave.sql']

# sql_queries=read_sql_file('./leavemgt/sql/filter_and_insert_into_designation.sql')
# print(sql_queries)
