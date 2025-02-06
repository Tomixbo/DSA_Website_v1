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
        "validate_attendance": {"name": "Validate Attendance", "parent": None},
        "attendance_list": {"name": "Attendance Records", "parent": None},
        "display_code": {"name": "Attendance Code", "parent": None},
        "team_members": {"name": "Team Members", "parent": "contest_detail"},
        "list_teams": {"name": "Teams", "parent": "contest_detail"},
        "create_team": {"name": "Create Team", "parent": "contest_detail"},
    }

    # Supprime l'espace de noms s'il existe pour correspondre aux clés du breadcrumb_map
    url_name = f"{match.namespace}:{match.url_name}" if match.namespace else match.url_name

    if url_name in breadcrumb_map or match.url_name in breadcrumb_map:
        current_data = breadcrumb_map.get(url_name) or breadcrumb_map.get(match.url_name)

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
        elif match.url_name == "team_members" and "contest_id" in match.kwargs and "team_id" in match.kwargs:
            current_url = reverse(match.url_name, kwargs={
                "contest_id": match.kwargs["contest_id"],
                "team_id": match.kwargs["team_id"]
            })
        elif match.url_name == "list_teams" and "contest_id" in match.kwargs:
            current_url = reverse(match.url_name, kwargs={
                "contest_id": match.kwargs["contest_id"]
            })
        elif match.url_name == "create_team" and "contest_id" in match.kwargs:
            current_url = reverse(match.url_name, kwargs={
                "contest_id": match.kwargs["contest_id"]
            })
        else:
            current_url = reverse(url_name)

        breadcrumbs.append({"name": current_data["name"], "url": current_url})

        # Ajout du parent s'il existe
        while parent_url_name:
            parent_data = breadcrumb_map.get(f"{match.namespace}:{parent_url_name}") or breadcrumb_map.get(parent_url_name)
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
