import rules


@rules.predicate
def is_my_availability(user, availability):
    return availability.user == user if availability is not None else True
