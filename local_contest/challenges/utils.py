from .models import CustomUser, Performance
from django.utils import timezone

BETA_SCORE_PASS = 50
GAMMA_SCORE_PASS = 200
OMEGA_SCORE_PASS = 300

def calculate_score(user):

        parameter_mapping = {'Alpha': 1, 'Beta': 2, 'Gamma': 3, 'Omega': 4}
        level_mapping = {'Level1': 1, 'Level2': 2, 'Level3': 3, 'Level4': 4, 'Level5': 5, 'Level6': 6, 'Level7': 7, 'Level8': 8, 'Level9': 9, 'Level10': 10}
        
        total_score = 0
        performances = Performance.objects.filter(user=user, solved=True)
        for performance in performances:
            defined_file_category = performance.definedfile.level.challenge.category
            defined_file_level = performance.definedfile.level.name
            parameter = parameter_mapping.get(defined_file_category, 0)
            level = level_mapping.get(defined_file_level, 0)
            total_score += parameter * level

        return total_score

def get_time_last_perf(user):
     # Récente performance
    latest_performance = user.performance_set.order_by('-created_at').first()
    if latest_performance:
        latest_performance_date = latest_performance.created_at.timestamp()
    else:
        latest_performance_date = 0
    
    return latest_performance_date


def calculate_rank(user):
    user_score = user.score
    total_user = CustomUser.objects.all().count()
    higher_scores = CustomUser.objects.filter(score__gt=user_score).count()
    same_scores = CustomUser.objects.filter(score=user_score).count()
    # print("Higher_scores than you :", higher_scores)
    # print("Same_scores as you, you included : ", same_scores)
    
    my_last_perf_time = get_time_last_perf(user)
    my_join_date = user.date_joined.timestamp()
    
    # print(latest_performance_date)

    # Count user before you
    same_before_you = 0 
    if my_last_perf_time!=0:
        for customuser in CustomUser.objects.filter(score=user_score):
            if my_last_perf_time > get_time_last_perf(customuser):
                same_before_you += 1
    else:
        for customuser in CustomUser.objects.filter(score=user_score):
            if my_join_date > customuser.date_joined.timestamp():
                same_before_you += 1
    

    rank = higher_scores + same_before_you + 1 
    if rank == 0:
         rank = CustomUser.objects.all().count()
    return (rank, total_user)

def update_ranks():
    users = CustomUser.objects.all()
    for user in users:
        user.rank = calculate_rank(user)[0]
        user.save(update_fields=['rank'])

def update_score(user):
    user.score = calculate_score(user)
    user.save(update_fields=['score'])
    update_category(user)

def update_category(user):
    if user.category == "Alpha":
        if user.score >= BETA_SCORE_PASS:
            user.category = "Beta"
    elif user.category == "Beta":
        if user.score >= GAMMA_SCORE_PASS:
            user.category = "Gamma"
    elif user.category == "Gamma":
        if user.score >= OMEGA_SCORE_PASS:
            user.category = "Omega"
    user.save(update_fields=['category'])
