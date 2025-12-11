from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'event-categories', views.EventCategoryViewSet)
router.register(r'event-components', views.EventComponentInfoViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'time-effective', views.EventTimeEffectiveViewSet)
router.register(r'time-specials', views.EventTimeSpecialViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('fault_statistics_data/', views.fault_statistics_data),                                   # 故障事件统计
    path('fault_statistics_device_data/', views.fault_statistics_device_data),                     # 故障设备统计
    path('fault_statistics_maintenance_data/', views.fault_statistics_maintenance_data),           # 故障维护统计
    path('fault_statistics_level_data/', views.fault_statistics_level_data),                       # 故障等级统计
    path('fault_statistics_impact_project_data/', views.fault_statistics_impact_project_data),     # 故障影响项目统计
    path('fault_statistics_category_trend_data/', views.fault_statistics_category_trend_data),     # 故障分类趋势统计
    path('fault_statistics_device_unit_data/', views.fault_statistics_device_unit_data),           # 故障设备单元统计
    path('fault_statistics_annual_data/', views.fault_statistics_annual_data),                     # 故障年度统计
    path('maintenance_statistics_data/', views.maintenance_statistics_data),                       # 维护商统计
    path('maintenance_statistics_score_data/', views.maintenance_statistics_score_data),           # 维护商评分统计
    path('maintenance_statistics_score_table_data/', views.maintenance_statistics_score_table_data),  # 维护商评分表格统计
]

