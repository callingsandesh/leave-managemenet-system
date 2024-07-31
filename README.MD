
### Description of Each Folder

#### leave-management-system/
- **leavemgt/**: Django project for Leave Management
- **apidataupload/**: Django app for API data upload
- **user/**: Django app for JWT Authentication
- **visualization/**: Django app for Visualization

### Other Folders and Files
- **Templates/**: Folder for Django Templates
- **SQL/**: Folder for SQL scripts
- **.gitignore**: Git ignore file
- **manage.py**: Django management script
- **requirements.txt**: Python dependencies
- **Documentation.pdf**: Documentation of the project
- **.env.example**: The example of .env file
- **utils**: Folder for utility scripts
- **README.md**: Project README file
- ***DockerFile**: File to setup the docker container
- **docker-compose.yml**: File to run docker file and setup the insfrastructure 


# Docker containerize the application
 1. docker-compose build
 2. docker-compose up


# Getting Started with leave-management-system

This guide will walk you through the steps to create a new user and access the login page for the LEAVE-MANAGEMENT-SYSTEM Django project.

## Creating a New User

1. Open a terminal or command prompt.

2. Navigate to the directory where your Django project (`leavemgt`) is located.

3. Start the Django shell:
   ```bash
   python manage.py shell

4. In the Django shell, execute the following Python code to create a new user:

```python
from django.contrib.auth.models import User

# Replace 'newuser', 'newuser@example.com', and 'password123' with your desired values
user = User.objects.create_user(username='newuser', email='newuser@example.com', password='password123')
```

5.Verify that the user has been created successfully.

## Running the Development Server

1. In the same terminal or command prompt, run the Django development server:
```python
python manage.py runserver
```
2. The development server should start, and you'll see output similar to:

Django version x.y.z, using settings 'leavemgt.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.


3. Open a web browser and go to the following link to access the login page:

http://127.0.0.1:8000/user/login/

4. Enter the username (newuser) and password (password123) you created earlier to log in.

5. You should now have access to the LEAVE-MANAGEMENT-SYSTEM application.

