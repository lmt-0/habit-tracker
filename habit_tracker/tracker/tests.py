from django.test import TestCase
from django.contrib.auth.models import User
from .models import Habit, HabitLog
from datetime import date, timedelta
from .views import get_color

class HabitTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass')

    def create_boolean_habit(self):
        return Habit.objects.create(
            user=self.user,
            name="Exercise",
            is_numeric=False
        )

    def create_numeric_habit(self, direction='less'):
        return Habit.objects.create(
            user=self.user,
            name="Screen Time",
            is_numeric=True,
            good_threshold=2,
            okay_threshold=4,
            direction=direction
        )

    def test_boolean_habit_streak(self):
        habit = self.create_boolean_habit()
        today = date.today()
        for i in range(3):
            HabitLog.objects.create(habit=habit, date=today - timedelta(days=i), boolean_value=True)

        self.assertEqual(habit.current_streak(), 3)

        HabitLog.objects.create(habit=habit, date=today - timedelta(days=3), boolean_value=False)
        self.assertEqual(habit.current_streak(), 3)

    def test_numeric_habit_streak_less(self):
        habit = self.create_numeric_habit(direction='less')
        today = date.today()

        HabitLog.objects.create(habit=habit, date=today, numeric_value=1)  
        HabitLog.objects.create(habit=habit, date=today - timedelta(days=1), numeric_value=3)  
        HabitLog.objects.create(habit=habit, date=today - timedelta(days=2), numeric_value=5)

        self.assertEqual(habit.current_streak(), 1)

    def test_numeric_habit_streak_more(self):
        habit = self.create_numeric_habit(direction='more')
        habit.good_threshold = 10000
        habit.okay_threshold = 8000
        habit.save()

        today = date.today()

        HabitLog.objects.create(habit=habit, date=today, numeric_value=11000) 
        HabitLog.objects.create(habit=habit, date=today - timedelta(days=1), numeric_value=9000)
        HabitLog.objects.create(habit=habit, date=today - timedelta(days=2), numeric_value=7000)
        print(habit.current_streak())
        self.assertEqual(habit.current_streak(), 1)

    def test_get_color_numeric_less(self):
        habit = self.create_numeric_habit(direction='less')
        log = HabitLog.objects.create(habit=habit, date=date.today(), numeric_value=1.5)
        color = get_color(habit, log)
        self.assertEqual(color, 'green')

    def test_get_color_numeric_more(self):
        habit = self.create_numeric_habit(direction='more')
        habit.good_threshold = 10
        habit.okay_threshold = 5
        habit.save()

        log = HabitLog.objects.create(habit=habit, date=date.today(), numeric_value=8)
        color = get_color(habit, log)
        self.assertEqual(color, 'orange')

    def test_get_color_boolean(self):
        habit = self.create_boolean_habit()
        log = HabitLog.objects.create(habit=habit, date=date.today(), boolean_value=True)
        color = get_color(habit, log)
        self.assertEqual(color, 'green')

        log.boolean_value = False
        log.save()
        color = get_color(habit, log)
        self.assertEqual(color, 'red')

