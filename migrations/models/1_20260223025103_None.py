from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" UUID NOT NULL PRIMARY KEY,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255),
    "auth_provider" VARCHAR(20) NOT NULL DEFAULT 'LOCAL',
    "version" INT NOT NULL DEFAULT 1,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_users_email_133a6f" ON "users" ("email");
CREATE TABLE IF NOT EXISTS "user_profiles" (
    "id" UUID NOT NULL PRIMARY KEY,
    "starter_cv_path" VARCHAR(512),
    "summary" TEXT,
    "target_role" VARCHAR(255),
    "user_id" UUID NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "agent_tasks" (
    "id" UUID NOT NULL PRIMARY KEY,
    "task_type" VARCHAR(20) NOT NULL,
    "status" VARCHAR(13) NOT NULL DEFAULT 'QUEUED',
    "subjective_question" TEXT,
    "error_log" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "agent_tasks"."status" IS 'QUEUED: QUEUED\nRUNNING: RUNNING\nAWAITING_USER: AWAITING_USER\nCOMPLETED: COMPLETED\nFAILED: FAILED';
CREATE TABLE IF NOT EXISTS "llm_usage_logs" (
    "id" UUID NOT NULL PRIMARY KEY,
    "prompt_tokens" INT NOT NULL,
    "completion_tokens" INT NOT NULL,
    "total_tokens" INT NOT NULL,
    "model_name" VARCHAR(50) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" UUID REFERENCES "users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "=="
)
