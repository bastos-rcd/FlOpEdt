

def can_push_user_availability(user, availability_user_id):
    if user.has_perm("base.push_any_useravailability"):
        return True
    if availability_user_id is not None and user.has_perm(
        "base.push_my_useravailability"
    ):
        return user.id == availability_user_id
    return False


def can_view_user_availability(user, availability_user_id):
    if can_push_user_availability(user, availability_user_id):
        return True
    if user.has_perm("base.view_any_useravailability"):
        return True
    if availability_user_id is not None and user.has_perm(
        "base.view_my_useravailability"
    ):
        return user.id == availability_user_id
    return False
