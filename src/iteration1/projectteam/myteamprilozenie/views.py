from django.shortcuts import render, redirect
from django.db import transaction
from .models import Patient, MedicalHistory, Prediction
from .forms import PatientForm, MedicalHistoryForm

def home(request):
    return render(request, 'myteamprilozenie/home.html')


def register_patient(request):
    if request.method == 'POST': # Если форма отправлена то создаем форму с данными из пост
        form = PatientForm(request.POST)
        if form.is_valid(): # Если форма правильная то сохраняем данные в бд
            patient = form.save()
            request.session['patient_id'] = patient.patient_id  # сохраняем айди в сессии чтобы работать с другими формами
            return redirect('myteamprilozenie:medical_history')
    else:
        form = PatientForm()

    return render(
        request,
        'myteamprilozenie/register_patient.html',  # Полный путь
        {'form': form} # Передаем форму в шаблон
    )


def medical_history(request):
    patient_id = request.session.get('patient_id') # Получаем как раз тот самый айди из открытой сессии
    if not patient_id:
        return redirect('register_patient') # Если айди не находит в сессии, то на форму регистрации

    try:
        patient = Patient.objects.get(pk=patient_id) # ищем пациента в базе данных
    except Patient.DoesNotExist:
        return redirect('register_patient') # если нет, то тоже на регистрацию

    if request.method == 'POST':
        form = MedicalHistoryForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                medical_data = form.save(commit=False)
                medical_data.patient = patient
                medical_data.save() # Сохраняем только после того как форма привяжется к айди пациента

                # Заглушка для ML модели
                prediction = Prediction.objects.create(
                    patient=patient,
                    medical_history=medical_data,
                    probability=0.0,
                    risk_level='M'
                )
                return redirect('myteamprilozenie:prediction_result', prediction_id=prediction.pk)

    else:
        form = MedicalHistoryForm()

    return render(request, 'myteamprilozenie/medical_history.html', {
        'form': form,
        'patient': patient
    })

# Здесь уже итоговый прогноз
def prediction_result(request, prediction_id):
    try:
        prediction = Prediction.objects.select_related('patient', 'medical_history').get(pk=prediction_id)
    except Prediction.DoesNotExist:
        return redirect('register_patient')

    return render(request, 'myteamprilozenie/predictions.html', {'prediction': prediction})