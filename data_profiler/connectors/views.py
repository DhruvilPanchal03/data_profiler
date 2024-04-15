from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .db import get_connection
from .models import my_connector,PostgresConnector
import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO

@login_required(login_url='login')
def check_conn(request):
    connector = get_object_or_404(my_connector, user=request.user)
    return render(request, 'conapp/connector.html', {'service': connector.service_name, 'connector_id': connector.id})

@login_required(login_url='login')
def select_conn(request, connector_id):
    connector = get_object_or_404(my_connector, id=connector_id)
    connection = get_connection(connector.username, connector.host, connector.password)
    if connection and connection.is_connected():
        messages.success(request, 'Connected to MySQL database successfully')
        return redirect('conlist')
    
    messages.error(request, 'Failed to connect to MySQL database')
    return redirect('connectors')


@login_required
def connectors(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        host = request.POST.get('host')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            messages.warning(request, 'Confirm password did not match')
        else:
            connection = get_connection(username, host, password)
            if connection and connection.is_connected():
                my_connector.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'username': username,
                        'password': password,
                        'host': host
                    }
                )
                messages.success(request, 'Connected to MySQL database successfully')
                return redirect('conlist')
            else:
                messages.error(request, 'Failed to connect to MySQL database')
    return render(request, 'conapp/connect.html')

def conlist(request):
    connection = get_connection_from_user(request.user)
    if connection and connection.is_connected():
        cursor = connection.cursor()
        cursor.execute('SHOW DATABASES')
        databases = [db[0] for db in cursor.fetchall()]
        return render(request, 'conapp/conlist.html', {'db': databases})
    return HttpResponse("Invalid credentials or no active connection")

def get_connection_from_user(user):
    connector = get_object_or_404(my_connector, user=user)
    return get_connection(connector.username, connector.host, connector.password)

def selectdatabase(request):
    if request.method == 'POST':
        selected_database = request.POST.get('selecteddatabase')
        request.session['selected_database'] = selected_database
        return redirect('tablelist')
    return HttpResponse("Invalid request method")

def tablelist(request):
    selected_database = request.session.get('selected_database')
    connection = get_connection_from_user(request.user)
    if connection and connection.is_connected():
        cursor = connection.cursor()
        cursor.execute(f'USE {selected_database}')
        cursor.execute('SHOW TABLES')
        tables = [table[0] for table in cursor.fetchall()]
        return render(request, 'conapp/tables.html', {'table': tables})
    return HttpResponse("Invalid credentials or no active connection")

def select_table(request):
    if request.method == 'POST':
        selected_table = request.POST.get('selected_table')
        return redirect('selected_table', selected_table=selected_table)
    return HttpResponse("Invalid request method")

def selected_table(request, selected_table):
    selected_database = request.session.get('selected_database')
    connection = get_connection_from_user(request.user)
    if connection and connection.is_connected():
        cursor = connection.cursor()
        cursor.execute(f'USE {selected_database}')
        cursor.execute(f'SELECT * FROM {selected_table}')
        table_data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(table_data, columns=columns)
        
        
        metrics = {
            'total_rows': len(df),
            'columns_count': len(df.columns),
            'null_values': df.isnull().sum().sum(),
            'null_values_per_column': df.isnull().sum(),
            'duplicate_values_per_column': {col: sum(df[col].duplicated()) for col in df.columns}
            
        }
        # Generating charts
        plt.figure(figsize=(10, 6))

        # Bar chart
        plt.subplot(1, 2, 1)
        df_count = df.apply(lambda x: x.value_counts().count())
        df_count.plot(kind='bar')
        plt.title('Unique Values Count')
        plt.xlabel('Columns')
        plt.ylabel('Count')

        # Pie chart
        plt.subplot(1, 2, 2)
        df_null = df.isnull().sum()
        df_null.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Null Values Percentage')

        # Save plot to bytes buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode plot to base64 string
        image_base64 = base64.b64encode(image_png).decode('utf-8')

        # Display the charts in HTML template

        return render(request, 'conapp/selected_table.html', {'table_data': table_data, 'columns': columns,'selected_table': selected_table, 'metrics': metrics, 'image_base64':image_base64})
    return HttpResponse("Invalid credentials or no active connection")

# def table_view(request):
#     selected_database = request.session.get('selected_database')
#     selected_table = request.session.get('selected_table')
#     connection = get_connection_from_user(request.user)
#     if connection and connection.is_connected():
#         cursor = connection.cursor()
#         cursor.execute(f'USE {selected_database}')
#         cursor.execute(f'SELECT * FROM {selected_table}')
#         table_data = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description]
#         return render(request, 'conapp/table.html', {'table_data': table_data, 'columns': columns, 'selected_table': selected_table})
#     return HttpResponse("Invalid credentials or no active connection")



# def etl_process(request,selected_table):
#     selected_database = request.session.get('selected_database')
#     connection = get_connection_from_user(request.user)
#     if connection and connection.is_connected():
#         # Extract data from the selected table
#         cursor = connection.cursor()
#         cursor.execute(f'USE {selected_database}')
#         cursor.execute(f'SELECT * FROM {selected_table}')
#         table_data = cursor.fetchall()
#         columns = [desc[0] for desc in cursor.description]
        
#         # Transform the data if necessary
#         # For example, convert the fetched data into a pandas DataFrame
#         df = pd.DataFrame(table_data, columns=columns)
        
#         # Perform some transformations if needed
#         # For example, data cleaning, feature engineering, etc.
#         # df_cleaned = some_transformation_function(df)
        
#         # Load the transformed data into another destination (e.g., another table or file)
#         # For example, you can save it to a CSV file
#         # df_cleaned.to_csv('transformed_data.csv', index=False)
        
#         return render(request, 'conapp/selected_table.html', {'table_data': table_data, 'columns': columns,'selected_table': selected_table})  # Return the transformed DataFrame or any other output
#     return HttpResponse("Invalid credentials or no active connection")


def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        # Process the uploaded file as required
        handle_uploaded_file(uploaded_file)
        return HttpResponse("File uploaded successfully!")
    return render(request, 'conapp/upload_file.html')

def handle_uploaded_file(f):
    # Read the uploaded CSV file
    matrix_data = []
    try:
        decoded_file = f.read().decode('utf-8').splitlines()
        csv_reader = csv.reader(decoded_file)
        matrix_data = list(csv_reader)
        print(matrix_data)
    except Exception as e:
        return None, f"Error reading CSV file: {e}"

    # Perform matrix calculation (example: sum of all elements)
    try:
        matrix = np.array(matrix_data, dtype=float)
        result = np.sum(matrix)  # Example calculation, you can perform any matrix operation here
        print(matrix)
        print(result)
    except Exception as e:
        return None, f"Error performing matrix calculation: {e}"

    return matrix, result