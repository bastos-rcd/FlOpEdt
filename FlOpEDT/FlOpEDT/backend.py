import logging

from django.contrib.auth.backends import ModelBackend
from rules.permissions import has_perm, permissions

logger = logging.getLogger("rules")


class DjangoRulesBackend(ModelBackend):
    # def authenticate(self, request, username=None, password=None, **kwargs):
    #     print("azzzzzzzzzzzzzzzzzzzz")
    #     return super().authenticate(
    #         request, username=username, password=password, **kwargs
    #     )

    def has_perm(self, user, perm, *args, **kwargs):  # pylint: disable=arguments-differ
        logger.debug("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        logger.debug(permissions)
        return has_perm(perm, user, *args, **kwargs)

    def has_module_perms(self, user, app_label):  # pylint: disable=arguments-renamed
        print("aaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        print(permissions)
        return has_perm(app_label, user)