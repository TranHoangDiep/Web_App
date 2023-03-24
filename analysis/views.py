from django.shortcuts import render
from django.conf import settings
from analysis.utils import *
import pandas as pd
import os



# Create your views here.
def series(request):
    views_1 = pd.Series([90006, 101141, 97297, 117182, 99637])
    views_1 = pd.DataFrame({'views': views_1})
    views_1 = views_1.to_html()

    views_2 = pd.Series([90006, 101141, 97297, 117182, 99637], ['a', 'b', 'c', 'd', 'e'])
    views_2 = pd.DataFrame({'views': views_2})
    views_2 = views_2.to_html()

    views_3 = pd.read_csv(os.path.join(settings.MEDIA_ROOT, 'analysis/data_views.csv'), squeeze=True)
    views_3 = pd.DataFrame({'views': views_3})
    # views_3 = views_3.to_html()
    views_3_head = views_3.head().to_html()
    views_3_tail = views_3.tail().to_html()


    return render(request, 'analysis/series.html', {
        'views_1': views_1,
        'views_2': views_2,
        'views_3_head': views_3_head,
        'views_3_tail': views_3_tail,
    })


def work_with_chart(request):
    # Histogram
    data_second = pd.read_excel(os.path.join(settings.MEDIA_ROOT, 'analysis/dataset.xlsx'), sheet_name='Wait_times')
    hist = get_hist(data_second, 'seconds', "Customer Wait Time")

    # Boxplot
    data_salaries = pd.read_excel(os.path.join(settings.MEDIA_ROOT, 'analysis/salaries.xlsx'))
    boxplot = get_box(data_salaries, 'salary', 'Salary')

    return render(request, 'analysis/chart.html', {
        'hist': hist,
        'boxplot': boxplot,
    })