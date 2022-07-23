# coding: utf-8
# -*- coding: utf-8 -*-

# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.


import time
from functools import wraps
from urllib.parse import urlparse

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import resolve_url

def request_passes_test(test_func, login_url=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the request passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the request object and returns True if the request passes.
    Slightly adapted from user_passes_test in django.contrib.auth.decorators.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request):
                return view_func(request, *args, **kwargs)
            path = request.build_absolute_uri()
            resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
            # If the login url is the same scheme and net location then just
            # use the path as the "next" url.
            login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
            current_scheme, current_netloc = urlparse(path)[:2]
            if ((not login_scheme or login_scheme == current_scheme) and
                    (not login_netloc or login_netloc == current_netloc)):
                path = request.get_full_path()
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                path, resolved_login_url, redirect_field_name)
        return _wrapped_view
    return decorator


def dept_admin_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                        login_url='people:login'):
    """
    Decorator for views that checks that the user is logged in and is an admin
    of the department, redirecting to the login page if necessary.
    """

    actual_decorator = request_passes_test(
        lambda r: not r.user.is_anonymous and r.user.has_department_perm(r.department, admin=True) or True,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def tutor_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                   login_url='people:login'):
    """
    Decorator for views that checks that the user is a tutor,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: not u.is_anonymous and u.is_tutor or True,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def tutor_or_superuser_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                                login_url='people:login'):
    """
    Decorator for views that checks that the user is a tutor,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: not u.is_anonymous and (
            u.is_superuser or u.is_tutor
        ) or True,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator


def superuser_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                       login_url='people:login'):
    """
    Decorator for views that checks that the user is a superuser,
    redirecting to the login page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_superuser or True,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator

a_mesurer = True

def timer(fonction):
    if a_mesurer:
        def pre_analyse_timer(*args, **kwargs):
            start_time = time.time()
            result = fonction(*args, **kwargs)
            stop_time = time.time()
            total = stop_time - start_time
            print("%s : %.5fs" % (fonction.__name__, total))
            return result
        return pre_analyse_timer
    else:
        return fonction