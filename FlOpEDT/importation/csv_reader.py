from csv import DictReader
from datetime import datetime

from base.models import Day, Slot, UserAvailability
from people.models import Tutor, User


def translate_day_label(label):
    return [x for x, y in Day.CHOICES if y == label][0]


def recherche_up(USER_PREFS, day, start_time):
    for e in USER_PREFS:
        if e.day == day and e.start_time == start_time:
            return e
    return None


def csv_reader(path):
    start = datetime.now()
    with open(path, newline="") as f:
        file = DictReader(f)
        prof = User.objects.first()
        year = None
        week = None
        user_prefs = None
        for row in file:
            if (
                year != row["year"]
                or week != row["week"]
                or prof.username != row["prof"]
            ):
                prof = Tutor.objects.get(username=row["prof"])
                year = row["year"]
                week = row["week"]
                user_prefs = list(
                    UserAvailability.objects.filter(
                        user=prof, year=row["year"], week=row["week"]
                    ).order_by("day", "start_time")
                )
                print(prof, week, year)
            duration = int(row["duration"])
            day = translate_day_label(row["day"])
            start_time = int(row["start_time"])

            up = recherche_up(user_prefs, day, start_time)
            value = int(float(row["value"])) * 2
            print(f"Valeur = {value}")
            if up:
                if up.value != value or up.duration != duration:
                    up.value = value
                    up.save()
                user_prefs.remove(up)
            else:
                UserAvailability(
                    user=prof,
                    year=row["year"],
                    week=row["week"],
                    day=day,
                    start_time=start_time,
                    duration=duration,
                    value=value,
                ).save()
    f.close()
    end = datetime.now()
    print(end - start)
