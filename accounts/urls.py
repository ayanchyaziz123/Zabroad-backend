from django.urls import path
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

def health(_request):
    return JsonResponse({'status': 'ok'})

urlpatterns = [
    path('health/',         health,                                      name='health'),
    path('otp/send/',       views.send_otp,                              name='send_otp'),
    path('otp/verify/',     views.verify_otp,                            name='verify_otp'),
    path('password/forgot/',views.forgot_password,                       name='forgot_password'),
    path('password/reset/', views.reset_password,                        name='reset_password'),
    path('register/',       views.register,                              name='register'),
    path('login/',          views.ThrottledTokenObtainPairView.as_view(),name='login'),
    path('logout/',         views.logout,                                name='logout'),
    path('token/refresh/',  TokenRefreshView.as_view(),                  name='token_refresh'),
    path('me/',             views.me,                                    name='me'),
    path('change-password/', views.change_password,                      name='change_password'),
    path('profile/<int:user_id>/', views.public_profile,                 name='public_profile'),
]
