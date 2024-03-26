from dateutil.rrule import FR, MO, MONTHLY, SA, SU, TH, TU, WE, WEEKLY, rrule
from django.db.models import F

from base.models import ScheduledCourse
from base.timing import days_index
from roomreservation.models import ReservationPeriodicity, RoomReservation

rrule_days = [MO, TU, WE, TH, FR, SA, SU]


def check_reservation(reservation_data):
    # convert time field in minute
    start_time = reservation_data['start_time']
    end_time = reservation_data['end_time']

    # date
    reservation_date = start_time.date()
    reservation_day_nb = reservation_date.weekday()
    room = reservation_data["room"]

    # filter
    all_room_courses = ScheduledCourse.objects.filter(version__major=0, room__in=room.and_overrooms())
    simultaneous_room_scheduled_courses = all_room_courses.filter(start_time__lt=end_time,
                                                                  start_time__gt=start_time - F('course__duration'))
    simultaneous_reservations = RoomReservation.objects.filter(room=room,
                                                               start_time__lt=end_time,
                                                               end_time__gt=start_time)

    if 'id' in reservation_data:
        simultaneous_reservations = simultaneous_reservations.exclude(pk=reservation_data['id'])

    simultaneous_slots = {'courses': [], 'reservations': []}
    if simultaneous_room_scheduled_courses.exists():
        simultaneous_slots['courses'] = [course.unique_name() for course in simultaneous_room_scheduled_courses]
    if simultaneous_reservations.exists():
        simultaneous_slots['reservations'] = [reservation.unique_name() for reservation in simultaneous_reservations]

    is_conflicting = len(simultaneous_slots['courses']) + len(simultaneous_slots['reservations']) > 0
    return {'status': 'NOK' if is_conflicting else 'OK', 'more': simultaneous_slots}


def check_periodicity(periodicity_data, reservation_data):
    result = {'status': 'OK', 'ok_reservations': [], 'nok_reservations': {}, 'periodicity_data': periodicity_data}
    start = periodicity_data["start"]
    end = periodicity_data["end"]
    periodicity_type = periodicity_data["periodicity_type"]
    if periodicity_type == ReservationPeriodicity.PeriodicityType.ByWeek:
        bw_weekdays = periodicity_data["bw_weekdays"]
        bw_weeks_interval = periodicity_data["bw_weeks_interval"]
        bw_integer_weekdays = [days_index[d] for d in bw_weekdays]
        considered_dates = list(rrule(WEEKLY,
                                      dtstart=start,
                                      until=end,
                                      byweekday=bw_integer_weekdays,
                                      interval=bw_weeks_interval))
    elif periodicity_type == ReservationPeriodicity.PeriodicityType.ByMonth:
        bm_x_choice = periodicity_data["bm_x_choice"]
        bm_day_choice = periodicity_data["bm_day_choice"]
        integer_bm_day_choice = days_index[bm_day_choice]
        byweekday_parameter = rrule_days[integer_bm_day_choice](bm_x_choice)
        considered_dates = list(rrule(MONTHLY,
                                      dtstart=start,
                                      until=end,
                                      byweekday=byweekday_parameter))
    else:
        date_nb = start.day
        considered_dates = list(rrule(MONTHLY,
                                      dtstart=start,
                                      until=end,
                                      bymonthday=date_nb))
    for date in considered_dates:
        considered_reservation = reservation_data.copy()
        days_difference = date - reservation_data['start_time'].date()
        considered_reservation['start_time'] += days_difference
        check = check_reservation(considered_reservation)
        # Format the date into a string
        if 'id' in considered_reservation:
            # Given reservation already exists, remove its id for the copies
            considered_reservation.pop('id')
        if check["status"] == 'OK':
            result['ok_reservations'].append(considered_reservation)
        else:
            result['status'] = 'NOK'
            result['nok_reservations'][considered_reservation['start_time'].date()] = check['more']
    return result
