import datetime as dt

from django.core.mail import send_mail
from django.utils import translation
from django.utils.html import strip_tags

from base.models import Course, Department, SchedulingPeriod
from TTapp.global_pre_analysis.tools_centralized_preanalysis import (
    get_flop_constraints_in_db,
)


def pre_analyse(department, period):
    """
    A global pre_analyse function that launches all "pre_analyse" on
    the existing TimetableConstraints.

    :param department: The department to search the TimetableConstraints applied on.
    :param period: The scheduling period to search the TimetableConstraints applied on.
    :return: A dictionary with the period exit status and a message explaining
    why it is impossible to create a timetable with the given data if the status is KO.
    If the status is KO for one pre_analyse, the loop stops and the resulting
    status is the KO status returned by the failed pre_analyse.
    """

    # Get all the active imperative constraints in the database
    all_constraints_list = get_flop_constraints_in_db(period, department)

    # Search for each TimetableConstraint's subclass
    # if we can find an instance of it for the given period and department
    result = []

    for constraint in all_constraints_list:
        try:
            json_dict = constraint.pre_analyse(period)
            if json_dict["status"] != "OK":
                # KO status found
                result.append(json_dict)
        except AttributeError:
            pass

    # All status returned by all pre-analysis iterations are OK
    json_dict = {
        "status": "OK",
        "messages": [],
        "period": {"id": period.id, "name": period.name},
    }

    return result


def pre_analyse_next_periods(department, nb_of_weeks):
    now = dt.datetime.now()
    considered_periods = SchedulingPeriod.objects.filter(
        start_date__lte=(now + dt.timedelta(days=7 * nb_of_weeks)).date(),
        mode=department.mode.scheduling_mode,
    )
    courses = Course.objects.filter(
        periods__in=considered_periods, type__department=department
    )
    result = {}
    considered_periods = list(c.period for c in courses.distinct("period"))
    for period in considered_periods:
        result[period] = pre_analyse(department=department, period=period)
        if not result[period]:
            result.pop(period)
    return result


def send_pre_analyse_email(department_abbrev, email_adress, nb_of_weeks=10):
    try:
        nb_of_weeks = int(nb_of_weeks)
    except ValueError:
        nb_of_weeks = 10
    translation.activate("fr")
    department = Department.objects.get(abbrev=department_abbrev)
    result = pre_analyse_next_periods(department, nb_of_weeks)
    if result:
        html_message = (
            "Voici les pré-analyses des prochaines semaines"
            f"pour le département {department.abbrev} :  <br />"
        )

        for period, dicts in result.items():
            html_message += f"&emsp; Période {period.name} : <br />"
            for json_dict in dicts:
                for message in json_dict["messages"]:
                    html_message += f"&emsp;&emsp; - {message['str']} <br />"
            html_message += "<br />"
        html_message += "<br /> <br /> "

        plain_message = strip_tags(html_message)
        send_mail(
            f"Pré-analyse des prochaines semaines ({department.abbrev})",
            plain_message,
            "",
            [email_adress],
            html_message=html_message,
            fail_silently=True,
        )
