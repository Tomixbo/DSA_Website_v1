from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.timezone import now
from django.contrib import messages
from attendance.models import AttendanceCode, UserAttendance

@user_passes_test(lambda u: u.is_superuser)
def display_code(request):
    code = AttendanceCode.objects.first()
    return render(request, 'attendance/display_code.html', {'code': code})



def validate_attendance(request):
    today = now().date()
    user = request.user

    # Vérifie si l'utilisateur a déjà marqué sa présence
    if UserAttendance.objects.filter(user=user, date=today).exists():
        return render(request, 'attendance/already_present.html')

    if request.method == "POST":
        input_code = request.POST.get('code', '').strip()
        generated_code = AttendanceCode.objects.first()

        if generated_code and input_code == generated_code.code:
            UserAttendance.objects.create(user=user, code_used=input_code)
            messages.success(request, "Votre présence a été validée avec succès !")
            return redirect('attendance:validate_attendance')
        else:
            messages.error(request, "Le code est incorrect. Veuillez réessayer.")

    return render(request, 'attendance/attendance_form.html')

@user_passes_test(lambda u: u.is_superuser)
def attendance_list(request):
    today = now().date()
    # Récupérer la liste des présences pour la date du jour
    attendance_records = UserAttendance.objects.filter(date=today)
    return render(request, 'attendance/attendance_list.html', {'attendance_records': attendance_records})
