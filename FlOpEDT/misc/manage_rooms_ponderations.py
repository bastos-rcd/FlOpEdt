from FlOpEDT.decorators import timer
from base.models import RoomPonderation, RoomType

@timer
def all_room_types_subsets_with_corresponding_basic_rooms(room_types_query_set):
    RT = room_types_query_set
    total = RT.count()
    result = {1:{}}
    for rt in RT:
        result[1][(rt,)] ={'all':rt.basic_rooms(), 'common':rt.basic_rooms()}
    again = True
    i = 1
    while again and i < total:
        i += 1
        again = False
        result[i] = {}
        for rt_tuple in result[i-1].keys():
            for new_rt in RT.filter(id__gt=rt_tuple[0].id):
                new_common_basic_rooms = new_rt.basic_rooms() & result[i-1][rt_tuple]["common"]
                if new_common_basic_rooms:
                    new_rt_tuple = (new_rt, *rt_tuple)
                    result[i][new_rt_tuple] = {}
                    result[i][new_rt_tuple]["common"] = new_common_basic_rooms
                    result[i][new_rt_tuple]["all"] = new_rt.basic_rooms() | result[i-1][rt_tuple]["all"]
                    again = True
    final_result = {key: result[i][key] for i in result for key in result[i]}
    return final_result


@timer
def room_types_subsets_with_ponderations_for_constraints(room_types_subsets_with_corresponding_basic_rooms):
    RTS = room_types_subsets_with_corresponding_basic_rooms
    result={}
    for room_types_tuple in RTS:
        basic_rooms = RTS[room_types_tuple]["all"]
        if not basic_rooms:
            result[room_types_tuple] = list(1 for _ in room_types_tuple)
        else:
            result[room_types_tuple] = list(max(len(room.basic_rooms() & basic_rooms)
                                                for room in rt.members.all())
                                            for rt in room_types_tuple)
    return result

@timer
def register_ponderations_in_database(department):
    room_types_query_set = RoomType.objects.filter(department=department)
    room_types_to_update = room_types_query_set.exclude(course__isnull=True)
    ARTS = all_room_types_subsets_with_corresponding_basic_rooms(room_types_to_update)
    RTSWP = room_types_subsets_with_ponderations_for_constraints(ARTS)
    for rtswp in RTSWP:
        RP, created = RoomPonderation.objects.get_or_create(department=department, room_types=[rt.id for rt in rtswp])
        RP.ponderations = RTSWP[rtswp]
        RP.save()
    room_types_to_delete = room_types_query_set.filter(course__isnull=True)
    room_types_to_delete.delete()