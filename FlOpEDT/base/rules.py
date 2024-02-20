import rules


@rules.predicate
def is_my_availability(user, availability):
    return True
    print("~~~~~~~~~~~~~~")
    print(availability)
    return availability.user == user
