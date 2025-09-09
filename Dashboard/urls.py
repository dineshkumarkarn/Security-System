from django.urls import path
from Dashboard import views


   
urlpatterns = [
    
    path('', views.index, name='index'),
    path('start_detection/', views.start_detection, name='start_detection'),
    path('start_normal/', views.start_normal, name="start_normal"),
    path('start_mobile_detection/', views.start_mobile_detection, name="start_mobile_detection"),
    path('start_mobile_normal/', views.start_mobile_normal, name="start_mobile_normal"),
    path("start_face/", views.start_face, name="start_face"),
    path("add_face/", views.add_face, name="add_face"),
    path('anomaly_stream/', views.anomaly_stream, name='anomaly_stream'),
    path('all_anomalies/', views.all_anomalies, name='all_anomalies'),
    path('alert_status/', views.alert_status, name='alert_status'),
]
   

