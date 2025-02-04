from django.urls import resolve, reverse

def breadcrumb_context(request):
    match = resolve(request.path)
    breadcrumbs = [{"name": "Home", "url": reverse("post_list")}]

    breadcrumb_map = {
        "challenge_list": {"name": "Challenges", "parent": None},
        "challenge_detail": {"name": "Challenge Details", "parent": "challenge_list"},
        "contest_list": {"name": "Contests", "parent": None},
        "contest_detail": {"name": "Contest Details", "parent": "contest_list"},
        "contest_challenge_detail": {"name": "Contest Challenge", "parent": "contest_detail"},
        "contest_inscription": {"name": "Contest Registration", "parent": "contest_detail"},
        "contest_participate": {"name": "Contest Participation", "parent": "contest_detail"},
        "contest_leaderboard": {"name": "Contest Leaderboard", "parent": "contest_detail"},
        "ranking": {"name": "Ranking", "parent": None},
        "attendance_list": {"name": "Attendance Records", "parent": None},
        "display_code": {"name": "Attendance Code", "parent": None},
        "validate_attendance": {"name": "Validate Attendance", "parent": None},
    }

    if match.url_name in breadcrumb_map:
        current_data = breadcrumb_map[match.url_name]
        parent_url_name = current_data.get("parent")
        
        # Génération de l'URL dynamique pour les vues qui nécessitent un ID
        if match.url_name in ["contest_detail", "contest_inscription", "contest_participate", "contest_leaderboard"] and "contest_id" in match.kwargs:
            current_url = reverse(match.url_name, kwargs={"contest_id": match.kwargs["contest_id"]})
        elif match.url_name == "contest_challenge_detail" and "contest_id" in match.kwargs and "challenge_slug" in match.kwargs:
            current_url = reverse(match.url_name, kwargs={
                "contest_id": match.kwargs["contest_id"],
                "challenge_slug": match.kwargs["challenge_slug"]
            })
        elif match.url_name == "challenge_detail" and "challenge_slug" in match.kwargs:
            current_url = reverse(match.url_name, kwargs={"challenge_slug": match.kwargs["challenge_slug"]})
        else:
            current_url = reverse(match.url_name)

        breadcrumbs.append({"name": current_data["name"], "url": current_url})

        # Ajout du parent s'il existe
        while parent_url_name:
            parent_data = breadcrumb_map.get(parent_url_name)
            if not parent_data:
                break
            
            if parent_url_name == "contest_detail" and "contest_id" in match.kwargs:
                parent_url = reverse(parent_url_name, kwargs={"contest_id": match.kwargs["contest_id"]})
            elif parent_url_name == "challenge_detail" and "challenge_slug" in match.kwargs:
                parent_url = reverse(parent_url_name, kwargs={"challenge_slug": match.kwargs["challenge_slug"]})
            else:
                parent_url = reverse(parent_url_name)
            
            breadcrumbs.insert(1, {"name": parent_data["name"], "url": parent_url})
            parent_url_name = parent_data.get("parent")

    return {"breadcrumbs": breadcrumbs}
