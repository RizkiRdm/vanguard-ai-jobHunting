# Project Development Log

- 2026-05-08: Migrated `VanguardAI.check_budget_limit` and `VanguardAI._log_token_usage` from Tortoise ORM to SQLAlchemy 2.0. Updated `core/ai_agent.py` and `core/orchestrator.py`.
- 2026-05-08: Aligned `modules/agent/agent_router.py` field names (`metadata` → `meta_data`) and fixed screenshot path lookup.
- 2026-05-08: Updated `UI/index.html` to dynamically derive `user_id` from JWT `sub` claim, removing hardcoded `user1`.
- 2026-05-08: Hardened task queue by adding `tests/test_task_manager.py` and updating `claim_next_task` in `core/task_manager.py` to be testable with injected sessions.
