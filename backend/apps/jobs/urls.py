
from django.urls import path

from . import views

urlpatterns = [
    path("jobs/inspect/", views.inspect_job, name="inspect-job"),
    path(
        "jobs/<str:job_id>/fill/",
        views.fill_job,
        name="fill-job",
    ),
    path("test-form/", views.test_form, name="test-form"),
]
