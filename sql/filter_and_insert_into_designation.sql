
    -- Insert filtered results from source_table to destination_table
    INSERT INTO apidataupload_designation(id, name)
    SELECT DISTINCT "designationId", "designationName"
    FROM apidataupload_employeeleave a
    WHERE a."designationId" NOT IN
    (
        SELECT DISTINCT "designationId" FROM apidataupload_designation
    );




