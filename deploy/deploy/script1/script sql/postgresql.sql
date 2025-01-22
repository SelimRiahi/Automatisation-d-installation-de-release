CREATE EXTENSION IF NOT EXISTS pgcrypto;
DO $$
DECLARE
    title VARCHAR(255);
    description TEXT;
BEGIN
    title := 'Task_' || LEFT(gen_random_uuid()::text, 6);
    description := 'Description of ' || title;

    EXECUTE 'CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        due_date DATE,
        completed BOOLEAN NOT NULL
    )';

    EXECUTE 'INSERT INTO tasks (title, description, due_date, completed)
    SELECT $1, $2, ''2024-03-21'', FALSE
    WHERE NOT EXISTS (
        SELECT 1 FROM tasks WHERE title = $1
    )' USING title, description;
END $$;