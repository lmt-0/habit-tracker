from django.shortcuts import render, redirect, get_object_or_404
from .models import Habit, HabitLog
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from datetime import date, timedelta, datetime
import calendar
from calendar import monthrange

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

@login_required
def dashboard(request):
    habits = Habit.objects.filter(user=request.user)
    return render(request, 'tracker/dashboard.html', {'habits': habits})

@login_required
def add_habit(request):
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_numeric = bool(request.POST.get('is_numeric'))

        good_threshold_raw = request.POST.get('good_threshold')
        okay_threshold_raw = request.POST.get('okay_threshold')
        good_threshold = float(good_threshold_raw) if good_threshold_raw else None
        okay_threshold = float(okay_threshold_raw) if okay_threshold_raw else None

        direction = request.POST.get('direction') if is_numeric else None

        habit = Habit.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_numeric=is_numeric,
            good_threshold=good_threshold,
            okay_threshold=okay_threshold,
            direction=direction
        )
        return redirect('dashboard')

    return render(request, 'tracker/add_habit.html')

@login_required
def habit_detail(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    first_day = date(year, month, 1)
    _, num_days = calendar.monthrange(year, month)

    if request.method == 'POST':
        log_date_str = request.POST.get('log_date')
        if log_date_str:
            try:
                log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date()
            except ValueError:
                log_date = today

            if log_date > date.today():
                return redirect('habit_detail', habit_id=habit.id)  

            log, _ = HabitLog.objects.get_or_create(habit=habit, date=log_date)

            if habit.is_numeric:
                value = request.POST.get('value')
                if value:
                    log.numeric_value = float(value)
                    log.save()
            else:
                done = request.POST.get('done')
                if done == '1':
                    log.boolean_value = True
                elif done == '0':
                    log.boolean_value = False
                log.save()

        return redirect(f'/habit/{habit.id}/?month={month}&year={year}')

    calendar_data = []
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        log = HabitLog.objects.filter(habit=habit, date=d).first()

        if log:
            value = log.numeric_value if habit.is_numeric else log.boolean_value
        else:
            value = None
      
        colour = get_colour(habit, log)

        calendar_data.append({
            'today': date.today(),
            'day': day,
            'date': d,
            'log': log,
            'value': value,
            'colour': colour,
        })

    first_weekday = first_day.weekday()  # 0 = monday
    padded_data = [None] * first_weekday + calendar_data
    end_padding = (7 - len(padded_data) % 7) % 7
    padded_data += [None] * end_padding
    weeks = [padded_data[i:i+7] for i in range(0, len(padded_data), 7)]

    prev_month = (first_day.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)

    context = {
        'today': date.today(),
        'habit': habit,
        'weeks': weeks,
        'streak': habit.current_streak(),
        'month_name': first_day.strftime('%B'),
        'year': year,
        'prev_month': prev_month,
        'next_month': next_month,
        'prev_month_name': prev_month.strftime('%B'),
        'next_month_name': next_month.strftime('%B'),
    }

    return render(request, 'tracker/habit_detail.html', context)

# must set 'good' threshold, 'okay' optional
# TODO, should probs clean this up 
# (◉︵◉)

def get_colour(habit, habit_log):
    if habit is None:
        return "grey"
    if habit is not None:
        if habit_log.boolean_value == True:
            return "green"
        elif habit_log.boolean_value == False:
            return "red"
        else:
            if habit.good_threshold is not None and habit.okay_threshold is not None:
                if habit.is_numeric:
                    if not habit_log or habit_log.numeric_value is None or habit.direction not in ['less', 'more']:
                        return "grey"

                    value = habit_log.numeric_value
                    if habit.direction == 'less':
                        if value < habit.good_threshold:
                            return "green"
                        elif value < habit.okay_threshold:
                            return "orange"
                        else:
                            return "red"
                    else:  # direction == 'more'
                        if value >= habit.good_threshold:
                            return "green"
                        elif value >= habit.okay_threshold:
                            return "orange"
                        else:
                            return "red"
                else:
                    if not habit_log:
                        return "grey"
                    return "green" if habit_log.boolean_value else "red"
            elif habit.is_numeric:
                if habit.good_threshold is not None and habit.okay_threshold is None:
                    value = habit_log.numeric_value
                    if habit.direction == 'less':
                        if value < habit.good_threshold:
                            return "green"
                        else:
                            return "red"
                    else:
                        if value >= habit.good_threshold:
                            return "green"
                        else: 
                            return "red"
            else:
                return "grey"

@login_required
def delete_habit(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)

    if request.method == 'POST':
        habit.delete()
        return redirect('dashboard')  

    return render(request, 'tracker/confirm_delete.html', {'habit': habit})

