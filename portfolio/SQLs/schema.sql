CREATE TABLE IF NOT EXiSTS"users"(
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "username" TEXT NOT NULL UNIQUE,
    "password_hash" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "email" TEXT NOT NULL UNIQUE,
    "role" TEXT NOT NULL,
    "headline" TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS "about"(
    "user_id" INTEGER PRIMARY KEY,
    "about_me" TEXT,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);

