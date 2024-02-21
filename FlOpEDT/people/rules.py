import rules

import logging

logger = logging.getLogger("rules")


@rules.predicate
def is_theme_ok(user, theme) -> bool:
    print(user)
    print(theme.user)
    logger.debug("aaaaaazezaeazeaz")
    return user == theme.user


@rules.predicate
def is_user_ok(user, theme) -> bool:
    return True
