from django.urls import path
from .views import upload_resume, download_report, download_pdf_report
from . import views
urlpatterns = [
    path('', views.upload_resume, name='upload_resume'),
    path('download_report/', views.download_report, name='download_report'),
    path('download_pdf_report/', views.download_pdf_report, name='download_pdf_report'),
]
