CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY,
    github_id INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    description TEXT,
    language TEXT,
    stars INTEGER NOT NULL CHECK (stars >= 0),
    forks INTEGER NOT NULL CHECK (forks >= 0),
    open_issues INTEGER NOT NULL CHECK (open_issues >= 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
