from django.urls import include, path

from .base.urls import routerConstraintBase

url_constraint_patterns = [
    path("base/", include(routerConstraintBase.urls), name="constraint"),
]
