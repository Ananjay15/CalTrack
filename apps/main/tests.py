from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.main.models import Goal, Level, Workout, Yoga, Food, MealType
from apps.main.services.helpers import (
    calculate_calories,
    split_meal_calories,
    greedy_workout_selector,
    greedy_food_selector,
    calculate_macros,
    get_goal_from_string,
)
from apps.main.services.workout import recommend_workout
from apps.main.services.yoga import recommend_yoga
from apps.main.services.diet import recommend_diet
from apps.accounts.models import Profile


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.goal = Goal.objects.create(name="Test Goal", slug="test-goal")

    def test_goal_str(self):
        self.assertEqual(str(self.goal), "Test Goal")

    def test_workout_creation(self):
        level = Level.objects.create(name="Beginner", slug="beginner")
        workout = Workout.objects.create(
            name="Push Ups",
            duration_minutes=10,
            calories_burned_per_minute=7.0,
            goal=self.goal,
            level=level,
            home_gym="home",
        )
        self.assertEqual(str(workout), "Push Ups")


class HelperFunctionTests(TestCase):
    def test_calculate_calories_weight_loss(self):
        result = calculate_calories(
            age=30,
            gender="male",
            height=180,
            weight=80,
            activity=1.55,
            goal=Goal(name="Weight Loss", slug="weight_loss"),
        )
        self.assertIn("bmi", result)
        self.assertIn("bmr", result)
        self.assertIn("target_calories", result)
        # BMR should be ~ 1775, maintenance ~ 2751, target ~ 2451 (deficit 300)
        self.assertEqual(result["recommendation"], "Weight Loss")
        self.assertLess(result["target_calories"], result["bmr"] * 1.55)

    def test_split_meal_calories_default(self):
        result = split_meal_calories(2000)
        self.assertEqual(result, {
            "breakfast": 500,
            "lunch": 700,
            "snack": 200,
            "dinner": 600,
        })

    def test_greedy_workout_selector(self):
        level = Level.objects.create(name="Intermediate", slug="intermediate")
        goal = Goal.objects.create(name="General", slug="general")
        # Create workouts with known burns
        w1 = Workout.objects.create(
            name="W1", duration_minutes=30, calories_burned_per_minute=10,
            goal=goal, level=level
        )  # total burn 300
        w2 = Workout.objects.create(
            name="W2", duration_minutes=20, calories_burned_per_minute=12,
            goal=goal, level=level
        )  # total burn 240
        w3 = Workout.objects.create(
            name="W3", duration_minutes=15, calories_burned_per_minute=8,
            goal=goal, level=level
        )  # total burn 120

        qs = Workout.objects.all()
        selected, total = greedy_workout_selector(qs, 250)
        # Greedy descending should pick W1 (300) first, then stop because 300 >= 250
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["workout"].name, "W1")
        self.assertGreaterEqual(total, 250)

    def test_greedy_food_selector(self):
        goal = Goal.objects.create(name="Test", slug="test")
        meal_type = MealType.objects.create(name="Lunch", slug="lunch")
        f1 = Food.objects.create(
            name="Rice", total_calories=200, protein_g=4, carbs_g=44, fats_g=1,
            goal=goal, meal_type=meal_type
        )
        f2 = Food.objects.create(
            name="Dal", total_calories=150, protein_g=10, carbs_g=20, fats_g=5,
            goal=goal, meal_type=meal_type
        )
        f3 = Food.objects.create(
            name="Salad", total_calories=50, protein_g=2, carbs_g=10, fats_g=0,
            goal=goal, meal_type=meal_type
        )
        qs = Food.objects.filter(meal_type__slug="lunch")
        selected, gap = greedy_food_selector(qs, 280)
        # Should pick smallest first: Salad(50), Dal(150), Rice(200) total=400 > 280? Wait ascending order picks smallest first: 50,150,200. It will pick 50+150=200, can't add 200 (exceed 280). So 2 items, gap 80.
        self.assertEqual(len(selected), 2)
        self.assertEqual(gap, 80)


class RecommendationEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="12345")
        cls.goal = Goal.objects.create(name="Weight Loss", slug="weight_loss")
        cls.level = Level.objects.create(name="Beginner", slug="beginner")
        cls.yoga_level = Level.objects.create(name="Intermediate", slug="intermediate")
        cls.profile = Profile.objects.create(
            user=cls.user,
            goal=cls.goal,
            target_calories=2000,
            level=cls.level,
            home_gym_preference="home",
            yoga_level=cls.yoga_level,
            diet_preference="veg",
            age=25,
            gender="female",
            height_cm=165,
            current_weight_kg=70,
            activity_level=1.375,
        )

        # Workouts
        cls.workout1 = Workout.objects.create(
            name="Home Workout",
            duration_minutes=20,
            calories_burned_per_minute=15,
            goal=cls.goal,
            level=cls.level,
            home_gym="home",
        )
        cls.workout2 = Workout.objects.create(
            name="Gym Workout",
            duration_minutes=30,
            calories_burned_per_minute=12,
            goal=cls.goal,
            level=cls.level,
            home_gym="gym",
        )

        # Yoga
        cls.yoga1 = Yoga.objects.create(
            name="Yoga Flow",
            duration_minutes=25,
            calories_burned_per_minute=6,
            goal=cls.goal,
            level=cls.level,
        )

        # Foods (veg)
        cls.meal_type_breakfast = MealType.objects.create(name="Breakfast", slug="breakfast")
        cls.meal_type_lunch = MealType.objects.create(name="Lunch", slug="lunch")
        cls.food1 = Food.objects.create(
            name="Oats",
            total_calories=300,
            protein_g=10,
            carbs_g=55,
            fats_g=5,
            goal=cls.goal,
            meal_type=cls.meal_type_breakfast,
            category="veg",
        )
        cls.food2 = Food.objects.create(
            name="Salad",
            total_calories=200,
            protein_g=8,
            carbs_g=30,
            fats_g=6,
            goal=cls.goal,
            meal_type=cls.meal_type_lunch,
            category="veg",
        )

    def test_recommend_workout_returns_selection(self):
        result = recommend_workout(self.profile)
        self.assertIn("workouts", result)
        # Should only pick home workout because of profile preference
        self.assertTrue(len(result["workouts"]) >= 1)
        # Check that gym workout is not in the result
        workout_names = [w["name"] for w in result["workouts"]]
        self.assertIn("Home Workout", workout_names)
        self.assertNotIn("Gym Workout", workout_names)

    def test_recommend_yoga_returns_sessions(self):
        result = recommend_yoga(self.profile)
        self.assertIn("yoga", result)
        self.assertGreaterEqual(len(result["yoga"]), 1)

    def test_recommend_diet_returns_plan(self):
        result = recommend_diet(self.profile)
        self.assertIn("breakfast", result)
        self.assertIn("lunch", result)
        self.assertIn("daily_macros", result)
        # Should have at least one food in breakfast if available
        self.assertTrue(len(result["breakfast"]["foods"]) >= 1)


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.user = User.objects.create_user(username="viewuser", password="testpass")
        cls.goal = Goal.objects.create(name="General Fitness", slug="general_fitness")

    def test_home_view_returns_200(self):
        response = self.client.get(reverse("main:home"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(response.status_code, 302)  # redirect to login

    def test_dashboard_logged_in(self):
        # Create profile for user
        Profile.objects.create(user=self.user, goal=self.goal)
        self.client.login(username="viewuser", password="testpass")
        response = self.client.get(reverse("dashboard:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "StrongP@ss1",
                "confirm_password": "StrongP@ss1",
                "goal": self.goal.pk,
            },
        )
        self.assertEqual(response.status_code, 302)  # redirect after signup
        self.assertTrue(User.objects.filter(username="newuser").exists())
        new_profile = Profile.objects.get(user__username="newuser")
        self.assertEqual(new_profile.goal, self.goal)