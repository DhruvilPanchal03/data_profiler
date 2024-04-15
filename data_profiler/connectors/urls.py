from django.urls import path
from . import views

urlpatterns = [
    path('check_conn/',views.check_conn,name='check_conn'),
    path('', views.connectors, name="connectors"),
    path('conlist/',views.conlist,name='conlist'),
    path('selectdatabase/',views.selectdatabase,name='selectdatabase'),
    path('tablelist/', views.tablelist, name='tablelist'),
    path('select_table/',views.select_table,name = 'select_table'),
    path('selected_table/<str:selected_table>/', views.selected_table, name='selected_table'),
    path('select_conn/<int:connector_id>', views.select_conn, name='select_conn'),
    path('upload/', views.upload_file, name='upload_file'),
    # path('table_view/', views.table_view, name='table_view'),
]