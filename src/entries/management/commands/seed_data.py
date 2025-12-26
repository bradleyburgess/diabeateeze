"""Management command to seed the database with sample data."""

import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from entries.models import GlucoseReading, InsulinDose, InsulinType, Meal

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with sample diabetes management data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days of data to generate (default: 30)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before seeding",
        )

    def handle(self, *args, **options):
        days = options["days"]
        clear_data = options["clear"]

        # Get or create a user
        user = User.objects.first()
        if not user:
            self.stdout.write(
                self.style.ERROR("No users found. Please create a user first.")
            )
            return

        if clear_data:
            self.stdout.write("Clearing existing data...")
            GlucoseReading.objects.all().delete()
            InsulinDose.objects.all().delete()
            Meal.objects.all().delete()
            InsulinType.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Existing data cleared"))

        # Create insulin types if they don't exist
        insulin_types = []
        for name, insulin_type in [
            ("Humalog", InsulinType.Type.RAPID_ACTING),
            ("NovoRapid", InsulinType.Type.RAPID_ACTING),
            ("Lantus", InsulinType.Type.LONG_ACTING),
            ("Levemir", InsulinType.Type.LONG_ACTING),
        ]:
            insulin, created = InsulinType.objects.get_or_create(
                name=name,
                defaults={
                    "type": insulin_type,
                    "is_default": name == "Humalog",
                    "last_modified_by": user,
                },
            )
            insulin_types.append(insulin)
            if created:
                self.stdout.write(f"Created insulin type: {name}")

        rapid_acting = [
            it for it in insulin_types if it.type == InsulinType.Type.RAPID_ACTING
        ]
        long_acting = [
            it for it in insulin_types if it.type == InsulinType.Type.LONG_ACTING
        ]

        # Generate data for the past N days
        now = timezone.now()
        glucose_count = 0
        insulin_count = 0
        meal_count = 0

        for day in range(days):
            date = now - timedelta(days=day)

            # Generate 4-6 glucose readings per day
            num_readings = random.randint(4, 6)
            reading_times = [
                date.replace(hour=7, minute=random.randint(0, 30)),  # Morning
                date.replace(hour=12, minute=random.randint(0, 30)),  # Noon
                date.replace(hour=18, minute=random.randint(0, 30)),  # Evening
                date.replace(hour=22, minute=random.randint(0, 30)),  # Night
            ]

            # Add extra readings randomly
            if num_readings > 4:
                reading_times.append(
                    date.replace(
                        hour=random.randint(9, 11), minute=random.randint(0, 59)
                    )
                )
            if num_readings > 5:
                reading_times.append(
                    date.replace(
                        hour=random.randint(15, 17), minute=random.randint(0, 59)
                    )
                )

            for reading_time in reading_times[:num_readings]:
                # Generate realistic glucose values (4.0-12.0 mmol/L)
                value = Decimal(str(round(random.uniform(4.0, 12.0), 1)))

                GlucoseReading.objects.create(
                    occurred_at=reading_time,
                    value=value,
                    unit="mmol/L",
                    notes=(
                        ""
                        if random.random() > 0.3
                        else random.choice(
                            [
                                "Before meal",
                                "After meal",
                                "Before exercise",
                                "Feeling low",
                                "Feeling high",
                            ]
                        )
                    ),
                    last_modified_by=user,
                )
                glucose_count += 1

            # Generate 3-4 insulin doses per day
            num_doses = random.randint(3, 4)
            dose_times = [
                date.replace(hour=7, minute=random.randint(30, 59)),  # Breakfast
                date.replace(hour=12, minute=random.randint(30, 59)),  # Lunch
                date.replace(hour=18, minute=random.randint(30, 59)),  # Dinner
                date.replace(
                    hour=22, minute=random.randint(30, 59)
                ),  # Bedtime (long-acting)
            ]

            for i, dose_time in enumerate(dose_times[:num_doses]):
                # Last dose of day is typically long-acting
                if i == num_doses - 1 and long_acting:
                    insulin = random.choice(long_acting)
                    base_units = Decimal(str(random.randint(15, 25)))
                    correction_units = Decimal("0")
                else:
                    insulin = random.choice(rapid_acting)
                    base_units = Decimal(str(random.randint(4, 10)))
                    correction_units = Decimal(str(random.randint(0, 4)))

                InsulinDose.objects.create(
                    occurred_at=dose_time,
                    base_units=base_units,
                    correction_units=correction_units,
                    insulin_type=insulin,
                    notes="" if random.random() > 0.2 else "With meal",
                    last_modified_by=user,
                )
                insulin_count += 1

            # Generate 3-4 meals per day
            meal_types = ["breakfast", "lunch", "dinner"]
            if random.random() > 0.5:
                meal_types.append("snack")

            meal_times = [
                date.replace(hour=7, minute=random.randint(0, 30)),  # Breakfast
                date.replace(hour=12, minute=random.randint(0, 30)),  # Lunch
                date.replace(hour=18, minute=random.randint(0, 30)),  # Dinner
            ]
            if len(meal_types) > 3:
                meal_times.append(
                    date.replace(
                        hour=random.randint(15, 16), minute=random.randint(0, 59)
                    )
                )

            meal_descriptions = {
                "breakfast": [
                    "Oatmeal with berries",
                    "Toast with eggs",
                    "Cereal with milk",
                    "Greek yogurt with granola",
                ],
                "lunch": [
                    "Sandwich with salad",
                    "Chicken and rice",
                    "Soup and bread",
                    "Pasta with vegetables",
                ],
                "dinner": [
                    "Grilled fish with vegetables",
                    "Stir-fry with noodles",
                    "Roasted chicken with potatoes",
                    "Beef stew",
                ],
                "snack": [
                    "Apple with peanut butter",
                    "Crackers and cheese",
                    "Protein bar",
                    "Nuts and dried fruit",
                ],
            }

            for meal_type, meal_time in zip(meal_types, meal_times):
                description = random.choice(meal_descriptions[meal_type])
                carbs = (
                    Decimal(str(random.randint(30, 80)))
                    if random.random() > 0.3
                    else None
                )

                Meal.objects.create(
                    occurred_at=meal_time,
                    meal_type=meal_type,
                    description=description,
                    total_carbs=carbs,
                    notes="" if random.random() > 0.2 else "Home cooked",
                    last_modified_by=user,
                )
                meal_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully seeded database with {days} days of data:\n"
                f"  - {glucose_count} glucose readings\n"
                f"  - {insulin_count} insulin doses\n"
                f"  - {meal_count} meals"
            )
        )
