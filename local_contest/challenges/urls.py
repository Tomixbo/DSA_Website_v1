from django.urls import path
from .views import challenge_detail, challenge_list, fetch_defined_files, get_user_rank, ranking

urlpatterns = [
    path('', challenge_list, name='challenge_list'),
    path('ranking/', ranking, name='ranking'),
    path('<str:challenge_slug>/', challenge_detail, name='challenge_detail'),
    path('<str:challenge_slug>/fetch-defined-files/', fetch_defined_files, name='fetch_defined_files'),
    path('<str:challenge_slug>/get_user_rank/', get_user_rank, name='get_user_rank'),
]
