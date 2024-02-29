import rules


@rules.predicate
def can_push_user_availability(user, availability):
    if user.has_perm("base.push_any_useravailability"):
        return True
    if user.has_perm("base.push_my_useravailability"):
        return availability.user == user
    return False
