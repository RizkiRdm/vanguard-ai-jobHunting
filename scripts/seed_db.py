import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import asyncio
from faker import Faker
from tortoise import Tortoise
from core.database import TORTOISE_CONFIG
from modules.profile.models import User, UserProfile
import sys
import os


# Tambahkan root directory ke path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fake = Faker()


async def run_seed(total_data: int = 10):
    print(f"[START] Seeding {total_data} data to database...")
    await Tortoise.init(config=TORTOISE_CONFIG)

    for i in range(total_data):
        fake_email = fake.unique.email()
        fake_job = fake.job()
        fake_summary = fake.paragraph(nb_sentences=3)

        user, created = await User.get_or_create(
            email=fake_email,
            defaults={
                "auth_provider": "LOCAL",
                "hashed_password": "hashed_password_here",
            },
        )

        if created:
            await UserProfile.create(
                user=user, target_role=fake_job, summary=fake_summary
            )
            print(f" {i+1}. ✅ Created: {fake_email}")
        else:
            print(f" {i+1}. ℹ️ Skipped: {fake_email} (Exists)")

    await Tortoise.close_connections()
    print("[END] Seeding finished.")


if __name__ == "__main__":
    asyncio.run(run_seed(total_data=100))
