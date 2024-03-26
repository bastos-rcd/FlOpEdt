from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from easter_egg.models import GameScore


def get_score(max_nb_score):
    score_list = [
        {"user": gs.user.username, "score": gs.score}
        for gs in GameScore.objects.order_by("-score")[:max_nb_score]
    ]
    if len(score_list) < max_nb_score:
        for s in range(len(score_list), max_nb_score):
            score_list.append({"user": "fake", "score": 0})
    return score_list


@csrf_exempt
def start_game(req):
    if not req.user.is_authenticated:
        return HttpResponse("Commencez par vous logger.")
    if req.method != "POST":
        return HttpResponse("Ce n'est pas si simple.")
    return render(req, "easter_egg/game.html", {"score_list": get_score(5)})


@login_required
def set_score(req, **kwargs):
    bad_response = HttpResponse(status=400)

    if (
        req.method != "POST"
        or req.META.get("HTTP_X_REQUESTED_WITH") != "XMLHttpRequest"
    ):
        return bad_response

    new_score = int(req.POST.get("score", "0"))

    result, created = GameScore.objects.get_or_create(
        user=req.user, defaults={"score": 0}
    )
    if created:
        result.score = new_score
    else:
        result.score = max(new_score, result.score)
    result.save()

    return JsonResponse(get_score(5), safe=False)


@login_required
def fetch_leaderboard(req):
    return JsonResponse(get_score(5), safe=False)
