import logging

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

from base.models import Department

logger = logging.getLogger(__name__)


class EdtContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(
        self, request, view_func, view_args, view_kwargs
    ):  # pylint: disable=unused-argument
        def del_request_department():
            try:
                del request.session[department_key]
            except KeyError:
                pass

        def set_request_department(
            request, department, set_session=True, set_cache=False
        ):
            request.department = department

            if set_session:
                session = request.session.get(department_key, "")
                if not session == department.abbrev:
                    logger.debug(
                        "store department %s in session with key %s",
                        department.abbrev,
                        department_key,
                    )
                    request.session[department_key] = department.abbrev

            if set_cache:
                logger.debug(
                    "store department %s in cache with key %s",
                    department.abbrev,
                    department_key,
                )
                cache.set(department_key, department)

        def set_request_department_prop(req):
            dept = req.department if hasattr(req, "department") else None
            req.has_department_perm = (
                req.user.is_authenticated and req.user.has_department_perm(dept)
            )
            req.is_department_admin = (
                req.user.is_authenticated
                and req.user.has_department_perm(dept, admin=True)
            )

        def get_department_abbrev(lookup_items):
            #
            # Lookup department abbrev from request collections
            #
            department_abbrev = ""

            for lookup_item in lookup_items:
                department_abbrev = lookup_item.get(department_key, "")
                if department_abbrev:
                    logger.debug("retrieve department from %s dictionnary", lookup_item)
                    return department_abbrev

            return department_abbrev

        department = None
        department_key = "department"

        if request.path == "/":
            del_request_department()
        else:
            # Lookup department abbrev
            department_abbrev = get_department_abbrev(
                (
                    view_kwargs,
                    request.GET,
                    request.session,
                )
            )

            if department_abbrev:
                # Lookup for a department cached item
                department = cache.get(department_key)
                logger.debug("get department from cache : %s", department)
                if department and department.abbrev == department_abbrev:
                    set_request_department(request, department)
                else:
                    try:
                        logger.debug(
                            "load department from database : %s", department_abbrev
                        )
                        department = Department.objects.get(abbrev=department_abbrev)
                        set_request_department(request, department, set_cache=True)
                    except ObjectDoesNotExist:
                        logger.warning("wrong department value : %s", department_abbrev)
                        return redirect("/")

        set_request_department_prop(request)

        if request.path.startswith("/admin"):
            if not department:
                # Check if the user is a superuser in order to
                # access global admin mode
                if request.user.is_authenticated and not request.user.is_superuser:
                    return redirect("/")
            else:
                # Check if the user is associated with the
                # requested department
                if not request.is_department_admin:
                    return HttpResponseForbidden()
