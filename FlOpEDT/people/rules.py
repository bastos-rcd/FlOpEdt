import rules


@rules.predicate
def is_ok(user, theme) -> bool:
    return user == theme.user


@rules.predicate
def is_user_ok(user, theme) -> bool:
    return True
