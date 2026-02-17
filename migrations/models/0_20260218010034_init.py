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
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmG1P2zAQgP9KlU8gMQThZWiaJoXSjU7QIggbAqHIjd02IrFD4lAq1P++s5v3t7WUQi"
    "vxpWrOd/Hd47Pv4hfFYZjY/va1TzzlW+NFocgh8Ccj32ooyHUTqRBw1LOlYgAaUoJ6PveQ"
    "yUHYR7ZPQISJb3qWyy1GQUoD2xZCZoKiRQeJKKDWY0AMzgaED6Ujd/cgtigmz8SPHt0Ho2"
    "8RG2f8tLCYW8oNPnal7Pq6ffJTaorpeobJ7MChibY75kNGY/UgsPC2sBFjA0KJhzjBqTCE"
    "l2G4kWjqMQi4F5DYVZwIMOmjwBYwlO/9gJqCQUPOJH72fyhz4DEZFWgtygWLl8k0qiRmKV"
    "XEVM1T7XJj73BTRsl8PvDkoCSiTKQh4mhqKrkmIImDLLvIsjlEXjnL2CCHE1xdDsgI0Ouo"
    "KQ56NmxCB3wIj7s7OzUY/2iXkiRoSZQM8nqa7Z1wSJ2OCaQJwiHyhwQbLvL9EfNKErMaZo"
    "npq7CG0GKqkUqCNdmby+CqHhzMwBW0KrnKsSxXFPCh4XrsycLT02hWqgXDt0nVWaAqZ92m"
    "drbALs9xnSVd1epsVQvJ+gTHtnCpgLNNeTnNlEWOI/i8LI67CxAciEm+qLv7X/eP9g73j0"
    "BFOhJLvtZAbXf0HDHTIyI4A/EitBMY4ZZDysllLXPwcGi6Hf1ZFsoF9znEgLvUHoenTA06"
    "vX3eutK18wsRieP7j7ZEpOktMaJK6Tgn3TjM5W78ksbftn7aEI+N226nlS9tsZ5+qwifYM"
    "8zg7KRgXCqikTSCExmYQMXv3Jhs5afC/uhCyudF41i/yHV4QhBD5kPI+RhozDCVFalmx1K"
    "sgXqSd+ySTFVjkPLLiU6g59LYiNefmCmuuuL5HUrV9snUb5H0jRlR3Vy6BxE0UA6Il4njE"
    "virPjISGGo/9YwQv6f3xzr/83hc+RxWFLzCTpf6HPmaO1KTNeyYT7YVWfo7ECrsrWTY9lO"
    "xQ8cB3njIk+dPFc0dymTNeFYV6daN3qmREW0Ns61m81MmTrrdn5F6im6zbPucQ4qJBwcFY"
    "bHys7+6kTNma0J3Hf4qpOH+XxHacrkfc/TpWXqfw7PhbqZLOoi56hPkazb4DGiZlmO5q4C"
    "V5RuoUkBsYdGcflOJw8EByERPt262lVTO2kpk5rub85+RyOeZQ7LWp1wpLbLQYnOyrQ3lZ"
    "cCpbux5D4gXJEPvQF8k/uA6m6m8kalujhUX6ks8Wpq5SuD2BpzQAzV1xPgUi6iYUZOaMlt"
    "xu+rbqfiiioxyYG8phDgHbZMvtWwLZ/frybWGooi6vp2MN/55aqxeMHxouV40fIy+Qc4fO"
    "VD"
)
