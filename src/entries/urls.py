from django.urls import path
from . import views

app_name = "entries"

urlpatterns = [
    path("quick/", views.quick_add, name="quick_add"),
    path("activity/", views.activity, name="activity"),
    path("readings/", views.glucose_readings_list, name="glucose_readings_list"),
    path("readings/add/", views.glucose_reading_create, name="glucose_reading_create"),
    path(
        "readings/<uuid:pk>/edit/",
        views.glucose_reading_edit,
        name="glucose_reading_edit",
    ),
    path("meals/", views.meals_list, name="meals_list"),
    path("meals/add/", views.meal_create, name="meal_create"),
    path("meals/<uuid:pk>/edit/", views.meal_edit, name="meal_edit"),
    path("doses/", views.insulin_doses_list, name="insulin_doses_list"),
    path("doses/add/", views.insulin_dose_create, name="insulin_dose_create"),
    path("doses/<uuid:pk>/edit/", views.insulin_dose_edit, name="insulin_dose_edit"),
    path(
        "insulin-schedule/", views.insulin_schedules_list, name="insulin_schedules_list"
    ),
    path(
        "insulin-schedule/add/",
        views.insulin_schedule_create,
        name="insulin_schedule_create",
    ),
    path(
        "insulin-schedule/<uuid:pk>/edit/",
        views.insulin_schedule_edit,
        name="insulin_schedule_edit",
    ),
    path(
        "correction-scale/", views.correction_scales_list, name="correction_scales_list"
    ),
    path(
        "correction-scale/add/",
        views.correction_scale_create,
        name="correction_scale_create",
    ),
    path(
        "correction-scale/<uuid:pk>/",
        views.correction_scale_edit,
        name="correction_scale_edit",
    ),
]
