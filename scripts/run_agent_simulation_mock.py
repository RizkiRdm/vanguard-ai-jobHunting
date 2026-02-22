import asyncio
import os
import uuid
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tortoise import Tortoise
from core.database import TORTOISE_CONFIG
from core.browser import BrowserManager
from core.task_manager import claim_next_task, update_task_status
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import User


# --- DUMMY AI AGENT ---
class DummyVanguardAI:
    """Simulasi AI tanpa memanggil API Gemini asli."""

    async def analyze_screen(self, screenshot_path: str, goal: str):
        print(f"   [MOCK AI] Analyzing screenshot: {os.path.basename(screenshot_path)}")
        await asyncio.sleep(1.5)  # Simulasi waktu berpikir AI

        # Simulasi keputusan cerdas berdasarkan 'goal'
        return {
            "action": "click",
            "selector": "button#example-about",
            "value": "",
            "reasoning": f"Found an element that looks like the About button to achieve: {goal}",
        }


# --- SIMULATION LOGIC ---
async def setup_simulation_data():
    """Menyiapkan data dummy di PostgreSQL."""
    print("📋 [1/5] Preparing Database Records...")
    user, _ = await User.get_or_create(
        email="dev_tester@vanguard.ai",
        defaults={"username": "dev_tester", "auth_provider": "LOCAL"},
    )

    # Hapus task lama agar bersih
    await AgentTask.filter(user=user).delete()

    task = await AgentTask.create(
        user=user, task_type="APPLYING", status=TaskStatus.QUEUED
    )
    print(f"✅ Created Task ID: {task.id}")
    return task


async def run_simulation():
    print("\n" + "=" * 50)
    print("🚀 VANGUARD AGENT: REAL-WORLD PIPELINE SIMULATION")
    print("=" * 50)

    await Tortoise.init(config=TORTOISE_CONFIG)
    await Tortoise.generate_schemas()

    try:
        # 1. Database Setup
        await setup_simulation_data()

        # 2. Claim Task (Uji Pessimistic Lock)
        print("\n🔍 [2/5] Claiming Task (Testing DB Lock)...")
        active_task = await claim_next_task()

        if not active_task:
            print("❌ No task available in queue.")
            return
        print(f"✅ Task {active_task.id} claimed and moved to RUNNING.")

        # 3. Browser Action
        print("\n🌐 [3/5] Starting Browser Context...")
        browser_mgr = BrowserManager(
            headless=False
        )  # Headless=False agar Anda bisa melihat
        ai_agent = DummyVanguardAI()  # Menggunakan Dummy

        async with browser_mgr.get_context() as context:
            page = await context.new_page()
            print("🔗 Navigating to https://example.com ...")
            await page.goto("https://example.com")

            # 4. Screenshot & AI Analysis
            print("\n📸 [4/5] Capturing State & Consulting Dummy AI...")
            screenshot_path = await browser_mgr.take_failure_screenshot(
                page, str(active_task.id)
            )

            decision = await ai_agent.analyze_screen(
                screenshot_path, "Find 'About' link"
            )

            print(
                f"🤖 AI Result: [{decision['action'].upper()}] on {decision['selector']}"
            )
            print(f"💡 Reason: {decision['reasoning']}")

            # Simulasi eksekusi sukses
            await asyncio.sleep(1)

            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

        # 5. Finalize State
        print("\n💾 [5/5] Finalizing Task State...")
        await update_task_status(active_task.id, TaskStatus.COMPLETED)
        print(f"🏁 SIMULATION FINISHED: Task {active_task.id} is now COMPLETED.")

    except Exception as e:
        print(f"\n💥 Simulation Error: {str(e)}")
        if "active_task" in locals() and active_task:
            await update_task_status(active_task.id, TaskStatus.FAILED, error=str(e))
    finally:
        await Tortoise.close_connections()
        print("=" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(run_simulation())
