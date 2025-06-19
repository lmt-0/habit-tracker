from django.db import models
from django.contrib.auth.models import User
from datetime import date

# can't import from views, circular :(
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


DIRECTION_CHOICES = [
    ('less', 'Less is better'),
    ('more', 'More is better'),
]

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  
    is_numeric = models.BooleanField(default=False)
    good_threshold = models.FloatField(null=True, blank=True)
    okay_threshold = models.FloatField(null=True, blank=True)
    direction = models.CharField(
        max_length=10,
        choices=DIRECTION_CHOICES,
        default='less',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    def current_streak(self):
        logs = self.habitlog_set.order_by('-date')
        streak = 0
     
        for log in logs:
            if self.is_numeric:
                if log.numeric_value is None:
                    break
            else:
                if log.boolean_value is None:
                    break

            colour = get_colour(self, log)
            if colour == 'green':
                streak += 1
            else:
                break

        return streak

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    boolean_value = models.BooleanField(null=True, blank=True)
    numeric_value = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ('habit', 'date')

