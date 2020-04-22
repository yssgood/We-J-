# We.J
An application that allows users to take turns sharing songs within music genre groups.

**GitHub Repository: https://github.com/arnavshah30/We.J**

### Building and Deploying

We assume that the user will be running the application on a suitable, modern web browser including: Chrome, Firefox, Edge. We also assume that the user has Python 3.7.4 and MySQL installed.

For database creation, run the SQL code found in [**databaseSchema.sql**](./databaseSchema.sql) on the MySQL server. For the
admin username use “**root**”, for the password use “**root**”, and for the port use **3306**. If you have already created an admin username and password for your MySQL Server, edit the application.py (lines 26, 27, 28) and fill in your credentials.

For deploying the application locally, we first need to install the packages found in requirements.txt. In the We.J directory, run the command “**pip install -r requirements.txt**”. Finally, run “**python application.py**” to locally deploy the application. The application can be accessed from a browser by pointing it to localhost:5000.

### Testing

In [**test_modules.py**](./tests/test_modules.py), change lines 10, 11, and 12 to your MySQL credentials. Navigate the terminal to the **tests** directory. Then run “**pytest**” to automatically run the tests (ensure that all required libraries from [**requirements.txt**](./requirements.txt) are already installed)

### User Documentation and Demonstration

Please see [**We.J User Documentation**](./documentation/We.J%20User%20Documentation.pdf) and [**We.J Video**](./documentation/We.J%20Video.mp4) for more information.
