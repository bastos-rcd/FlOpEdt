import rules

import logging

logger = logging.getLogger("rules")

from rules import is_authenticated


@rules.predicate
def is_theme_ok(user, theme) -> bool:
    print(user)
    print(theme.user)
    logger.debug("aaaaaazezaeazeaz")
    return user == theme.user


@rules.predicate
def is_theme_view_ok(user, theme) -> bool:
    if "people.view_any_themespreferences" in user.get_all_permissions():
        return True
    if "people.view_my_themespreferences" in user.get_all_permissions():
        return user == theme.user
    return False


@rules.predicate
def is_authenticated_tutor(user) -> bool:
    return user.is_authenticated and user.is_tutor
