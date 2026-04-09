# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.landing, name='builder_landing'),
#    # path('templates/', views.templates_view, name='builder_templates'),
#     path('form/', views.form_view, name='builder_form'),
#     path('preview/', views.preview_view, name='builder_preview'),
#     path('export/', views.export_view, name='builder_export'),

#     # NEW APIs
#     path('save-resume/', views.save_resume, name='save_resume'),
#     path('export-pdf/<int:resume_id>/', views.export_pdf, name='export_pdf'),
# ]

from django.urls import path
from . import views

urlpatterns = [

    path('', views.builder, name='builder'),
    path('feature/<slug:feature_slug>/', views.feature_detail, name='feature_detail'),
    path('save-resume/', views.save_resume, name='save_resume'),
    path('api/chat/', views.chat_bot, name='chatbot'),
    path('payments/razorpay/order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('payments/razorpay/verify/', views.verify_razorpay_payment, name='verify_razorpay_payment'),

]
