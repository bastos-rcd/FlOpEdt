from django.urls import path, include

from .base.urls import routerConstraintBase

url_constraint_patterns = [
    path("base/", include(routerConstraintBase.urls), name="constraint"),
]
