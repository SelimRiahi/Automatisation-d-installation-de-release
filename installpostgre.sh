DB_USER="postgres"
DB_PASSWORD="root"
DB_NAME="tasksdb"


SQL_COMMANDS="
BEGIN;
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    completed BOOLEAN NOT NULL
);
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM tasks) THEN
        INSERT INTO tasks (title, description, due_date, completed) VALUES
        ('Task 1', 'Description of task 1', '2024-03-01', FALSE),
        ('Task 2', 'Description of task 2', '2024-03-02', TRUE),
        ('Task 3', 'Description of task 3', '2024-03-03', FALSE),
        ('Task 4', 'Description of task 4', '2024-03-04', TRUE),
        ('Task 5', 'Description of task 5', '2024-03-05', FALSE);
    END IF;
END
\$\$;
COMMIT;
"

export PGPASSWORD=$DB_PASSWORD
psql -h localhost -U $DB_USER -d $DB_NAME -c "$SQL_COMMANDS"
unset PGPASSWORD
