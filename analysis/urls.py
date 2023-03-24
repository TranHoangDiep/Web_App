from django.urls import path
from analysis import views


app_name = 'analysis'
urlpatterns = [
    path('series/', views.series, name='series'),
    path('demo-chart/', views.work_with_chart, name='chart'),
]
