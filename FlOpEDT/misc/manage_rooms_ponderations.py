from core.decorators import timer
from base.models import RoomPonderation, RoomType
from django.db import transaction

@timer
def all_room_types_subsets_with_corresponding_basic_rooms(room_types_query_set):
    RT = room_types_query_set
    result = {'new': {}, 'old': {}}

    # Initialization: for each room_type, create a rt_tuple that unites all room_types
    # that have basic_rooms included in rt.basic_rooms()
    for rt in RT:
        basic_rooms = rt.basic_rooms()
        rt_set = {rt}
        for rt2 in set(RT)-{rt}:
            if rt2.basic_rooms().issubset(basic_rooms):
                rt_set.add(rt2)
        rt_tuple = convert_rt_set_to_sorted_tuple(rt_set)
        result['new'][rt_tuple] = basic_rooms

    # Then unit tuples that have common AND distinct rooms in a new tuple
    again = True
    while again:
        again = False
        new_keys = set(result["new"].keys())
        while new_keys:
            rt_tuple1 = new_keys.pop()
            basic_rooms_rt_tuple1 = result["new"].pop(rt_tuple1)
            result["old"][rt_tuple1] = basic_rooms_rt_tuple1
            for rt_tuple2 in new_keys:
                basic_rooms_rt_tuple2 = result["new"][rt_tuple2]
                intersection = basic_rooms_rt_tuple1 & basic_rooms_rt_tuple2
                # if basic_rooms are included one in one_other, or disjoints : do nothing
                if intersection in [basic_rooms_rt_tuple1, basic_rooms_rt_tuple2, set()]:
                    continue
                # else, create a new rt_tuple that unite previous ones, and unite basic_rooms
                else:
                    new_rt_tuple = unite_two_rt_tuples(rt_tuple1, rt_tuple2)
                    result["new"][new_rt_tuple] = basic_rooms_rt_tuple1 | basic_rooms_rt_tuple2
                    again = True

    # Finally, join tuples that have same basic rooms
    final_result = join_rt_tuples_in_dict_if_same_rooms(result['old'])

    return final_result


@timer
def room_types_subsets_with_ponderations_for_constraints(room_types_subsets_with_corresponding_basic_rooms):
    RTS = room_types_subsets_with_corresponding_basic_rooms
    result = {}
    for room_types_tuple in RTS:
        basic_rooms = RTS[room_types_tuple]
        if not basic_rooms:
            result[room_types_tuple] = list(1 for _ in room_types_tuple)
        else:
            result[room_types_tuple] = list(max(len(room.basic_rooms() & basic_rooms)
                                                for room in rt.members.all())
                                            for rt in room_types_tuple)
    return result


@transaction.atomic
@timer
def register_ponderations_in_database(department,
                                      only_used_room_types=True,
                                      delete_unused_room_types=False):
    RoomPonderation.objects.filter(department=department).delete()
    room_types_query_set = RoomType.objects.filter(department=department)
    room_types_to_update = room_types_query_set
    if only_used_room_types:
        room_types_to_update = room_types_query_set.exclude(course__isnull=True)

    ARTS = all_room_types_subsets_with_corresponding_basic_rooms(room_types_to_update)
    RTSWP = room_types_subsets_with_ponderations_for_constraints(ARTS)
    for rtswp in RTSWP:
        RP = RoomPonderation.objects.create(department=department, room_types=[rt.id for rt in rtswp])
        RP.ponderations = RTSWP[rtswp]
        RP.save()
    print(f"{len(RTSWP)} rooms ponderations created in database")
    if delete_unused_room_types:
        room_types_to_delete = room_types_query_set.filter(course__isnull=True)
        room_types_to_delete.delete()


def unite_two_rt_tuples(tuple1, tuple2):
    new_set = set(tuple1) | set(tuple2)
    return convert_rt_set_to_sorted_tuple(new_set)


def unite_rt_tuples(tuples_set):
    new_set = set()
    for tuple in tuples_set:
        new_set |= set(tuple)
    return convert_rt_set_to_sorted_tuple(new_set)


def convert_rt_set_to_sorted_tuple(rt_set):
    result = list(rt_set)
    result.sort(key=lambda x: x.id, reverse=True)
    return tuple(result)


def join_rt_tuples_in_dict_if_same_rooms(rt_tuples_dict):
    rt_tuples = set(rt_tuples_dict.keys())
    while rt_tuples:
        rt1 = rt_tuples.pop()
        basic_rooms_to_consider = rt_tuples_dict[rt1]
        tuples_to_merge = set()
        for rt2 in set(rt_tuples):
            if rt_tuples_dict[rt2] == basic_rooms_to_consider:
                tuples_to_merge.add(rt2)
                rt_tuples.remove(rt2)
        if tuples_to_merge:
            tuples_to_merge.add(rt1)
            new_tuple = unite_rt_tuples(tuples_to_merge)
            for t in tuples_to_merge:
                rt_tuples_dict.pop(t)
            rt_tuples_dict[new_tuple] = basic_rooms_to_consider

    return rt_tuples_dict
