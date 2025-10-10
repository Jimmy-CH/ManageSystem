
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'oa-infos', views.OAInfoViewSet, basename='oa-info')
router.register(r'oa-persons', views.OAPersonViewSet, basename='oa-person')
router.register(r'process-records', views.ProcessRecordViewSet)
router.register(r'entry-logs', views.EntryLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('submit-entry/', views.SubmitEntryApplicationView.as_view(), name='submit_entry'),
    path('summary/cards/', views.SummaryCardsView.as_view(), name='summary-cards'),
    path('summary/unit-distribution/', views.UnitDistributionView.as_view(), name='unit-distribution'),
    path('summary/applicant-count/', views.ApplicantCountView.as_view(), name='applicant-count'),
]
