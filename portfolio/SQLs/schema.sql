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

CREATE TABLE IF NOT EXISTS "skills"(
    "skill_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL,
    "skill_name" TEXT NOT NULL,
    "skill_content" TEXT NOT NULL,
    "skill_icon" TEXT NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);

CREATE TABLE IF NOT EXISTS "experience"(
    "experience_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL,
    "start_date" TEXT NOT NULL,
    "end_date" TEXT NOT NULL,
    "employer" TEXT NOT NULL,
    "role" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "tags" TEXT,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);

CREATE TABLE IF NOT EXISTS "projects"(
    "project_id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "user_id" INTEGER NOT NULL,
    "project_name" TEXT NOT NULL,
    "project_description" TEXT NOT NULL,
    "project_screenshot" TEXT,
    "project_url" TEXT,
    "tags" TEXT,
    "sort_order" INTEGER NOT NULL,
    FOREIGN KEY ("user_id") REFERENCES "users" ("id")
);
