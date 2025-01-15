from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('generate-script/', views.generate_script, name='generate_script'),
    path('save-script/', views.save_script, name='save_script'),
    path('saved-scripts/', views.saved_scripts, name='saved_scripts'),
    path('export-script/<int:script_id>/<str:file_format>/',
         views.export_script, name='export_script'),
    path('preview-file/', views.preview_file_content, name='preview_file'),
]
