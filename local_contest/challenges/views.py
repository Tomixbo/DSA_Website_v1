from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import DefinedFile, Challenge, Level, Performance, CustomUser
from django.db.models import Count, Subquery, OuterRef, Q
from django.contrib.auth.decorators import login_required
from .utils import calculate_rank, calculate_score, update_ranks, update_score, update_category
from contest.models import ContestChallenge
from django.utils.text import slugify
from django.shortcuts import render, redirect



def fetch_defined_files(request, challenge_slug):
    if request.method == 'GET':
        # Retrieve challenge based on the challenge_slug
        challenge = get_object_or_404(Challenge, slug=challenge_slug)
        level_id = request.GET.get('level_id')
        defined_files = DefinedFile.objects.filter(level__challenge=challenge, level_id=level_id)
        form_html = render_to_string('defined_file_form.html', {'defined_files': defined_files})
        return JsonResponse({'form_html': form_html})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
def challenge_detail(request, challenge_slug=None):
    update_ranks()
    user = request.user  # Obtenez l'utilisateur actuel
    rank, total_user = calculate_rank(user)
    update_category(user)
    if challenge_slug:
        defined_files = DefinedFile.objects.filter(level__challenge__slug=challenge_slug).order_by('name')
        test_results = {defined_file.id : defined_file.get_test_result_for_user(request) for defined_file in defined_files}
        challenge = get_object_or_404(Challenge, slug=challenge_slug)
        levels = Level.objects.filter(challenge=challenge).order_by('name')
        result = 'Upload your file first'
        if request.method == 'POST' :
            
            uploaded_file = request.FILES.get('uploaded_file')
            if uploaded_file:
                uploaded_content = uploaded_file.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')

                defined_file_name = request.POST.get('defined_file_name', None)

                if defined_file_name:
                    try:
                        defined_file = DefinedFile.objects.get(name=defined_file_name, level__challenge__name=challenge.name)
                        defined_content = defined_file.output_file.read().decode('utf-8').replace('\r\n', '\n').replace('\r', '\n').rstrip('\n')

                        if uploaded_content == defined_content:
                            performance = Performance.objects.create(user=user, definedfile=defined_file, solved=True)
                            result = 'VALID'
                            # print("Your score : ",calculate_score(user))
                            rank, total_user = calculate_rank(user)
                            # print("Your rank : ", rank, " sur ", total_user)
                            update_score(user)
                            update_ranks()
                        else:
                            update_score(user)
                            result = 'INVALID'

                    except DefinedFile.DoesNotExist:
                        update_score(user)
                        result = f'INVALID (No defined file named {defined_file_name} found for challenge : {challenge.name})'
                    
                    
                else:
                    update_score(user)
                    result = 'INVALID (No defined file name provided)'
            
            else:
                update_score(user)
                result = 'INVALID (No file uploaded)'
            return JsonResponse({'result': result})

        return render(request, 'challenge_detail.html', {'defined_files': defined_files, 'challenge': challenge, 'levels': levels, 'user': user, 'test_results': test_results, 'total_user': total_user})

    # Handle case when challenge name is not provided
    else:
        # Add logic here if needed
        return render(request, 'challenge_list.html', {'challenges': Challenge.objects.all(), 'user': user, 'total_user': total_user})



@login_required
def challenge_list(request):
    update_ranks()
    user = request.user
    update_category(user)

    # Exclure les challenges liés à un contest
    excluded_challenges = ContestChallenge.objects.values_list('challenge_id', flat=True)

    # Sous-requête pour compter tous les fichiers définis pour chaque challenge
    defined_files_count = Challenge.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        count=Count('levels__defined_files')
    ).values('count')

    # Sous-requête pour compter les fichiers définis résolus par l'utilisateur courant pour chaque challenge
    resolved_files_count = Challenge.objects.filter(
        pk=OuterRef('pk')
    ).annotate(
        count=Count('levels__defined_files', filter=Q(levels__defined_files__performance__user=user, levels__defined_files__performance__solved=True))
    ).values('count')

    # Appliquer le filtre pour exclure les challenges des contests
    challenges = Challenge.objects.exclude(id__in=excluded_challenges).order_by('category', 'name').filter(published=True).annotate(
        num_defined_files=Subquery(defined_files_count),
        num_resolved_defined_files=Subquery(resolved_files_count)
    )

    rank, total_user = calculate_rank(user)
    
    return render(request, 'challenge_list.html', {'challenges': challenges, 'total_user': total_user})



def get_user_rank(request, challenge_slug):
    user = request.user
    rank, total_user = calculate_rank(user)
    score = calculate_score(user)
    update_category(user)
    category = user.category
    return JsonResponse({'rank': rank, 'total_user': total_user, 'score': score, 'category': category})

@login_required
def ranking(request):
    update_ranks()
    user = request.user
    rank, total_user = calculate_rank(user)
    score = calculate_score(user)
    users = CustomUser.objects.order_by('rank').all()
    return render(request, 'ranking.html', {'user': user, 'users': users, 'rank': rank, 'total_user': total_user, 'score': score})

@login_required
def create_challenge(request):
    if request.method == "POST":
        # Débogage : Vérifier toutes les données envoyées
        print("Data reçue dans POST:", request.POST)
        print("Fichiers reçus dans FILES:", request.FILES)

        # Récupérer les infos du challenge
        name = request.POST.get("name")
        description = request.POST.get("description")
        author = request.POST.get("author")
        category = request.POST.get("category")
        difficulty = request.POST.get("difficulty")
        published = request.POST.get("published") == "on"

        # Créer et enregistrer le challenge
        challenge = Challenge.objects.create(
            name=name,
            slug=slugify(name),
            description=description,
            author=author,
            category=category,
            difficulty=difficulty,
            published=published
        )

        # Récupérer les levels
        level_count = int(request.POST.get("level_count", 0))
        print(f"Nombre de levels détectés : {level_count}")

        for i in range(1, level_count + 1):
            level_name = f"Level{i}"
            level_description = f"Level {i} for {name}"
            description_file = request.FILES.get(f"description_file_{i}")
            input_file = request.FILES.get(f"input_file_{i}")

            level = Level.objects.create(
                name=level_name,
                description=level_description,
                challenge=challenge,
                description_file=description_file,
                input_file=input_file
            )

            # Vérifions si le nombre de defined files est bien récupéré
            defined_file_count = int(request.POST.get(f"defined_file_count_{i}", 0))
            print(f"Level {i}: {defined_file_count} defined files détectés.")

            for j in range(1, defined_file_count + 1):
                defined_file_name = f"output{i}_{j}"
                input_file = request.FILES.get(f"defined_input_file_{i}_{j}")
                output_file = request.FILES.get(f"defined_output_file_{i}_{j}")

                # Débogage : Vérifier si les fichiers sont bien récupérés
                print(f"Tentative de création: {defined_file_name}")
                print(f"   ↳ input_file: {input_file}")
                print(f"   ↳ output_file: {output_file}")

                if input_file and output_file:
                    DefinedFile.objects.create(
                        name=defined_file_name,
                        level=level,
                        input_file=input_file,
                        output_file=output_file
                    )
                    print(f"DefinedFile {defined_file_name} créé avec succès.")
                else:
                    print(f"ERREUR: Les fichiers pour {defined_file_name} sont manquants!")

        return redirect("challenge_list")

    return render(request, "create_challenge.html")
