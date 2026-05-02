from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Tadbirlar
    path('', views.event_list, name='event_list'),
    path('event/<int:pk>/', views.event_detail, name='event_detail'),

    # Bron qilish
    path('book/<int:ticket_type_id>/', views.book_ticket, name='book_ticket'),
    path('booking/<int:pk>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:pk>/download/', views.download_ticket, name='download_ticket'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # Profil
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='event_list'), name='logout'),
]
