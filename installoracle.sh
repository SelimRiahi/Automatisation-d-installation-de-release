#!/bin/bash

DB_USER="system"
DB_PASSWORD="root"
DB_CONNECTION_STRING="//localhost:1521/xe"


SQLPLUS_CMD="sqlplus -s $DB_USER/$DB_PASSWORD@$DB_CONNECTION_STRING"


CHECK_EMPTY=$(
$SQLPLUS_CMD <<EOF
SET pagesize 0 feedback off verify off heading off echo off;
SELECT COUNT(*) FROM all_tables WHERE table_name = 'USERS';
EXIT;
EOF
)


if [[ $CHECK_EMPTY -eq 0 ]]; then
    SQL_COMMANDS="
    CREATE SEQUENCE users_seq
    START WITH 1
    INCREMENT BY 1
    NOCACHE
    NOCYCLE;
    CREATE TABLE users (
        id NUMBER PRIMARY KEY,
        username VARCHAR2(255) NOT NULL,
        password VARCHAR2(255) NOT NULL,
        email VARCHAR2(255) NOT NULL
    );
    CREATE OR REPLACE TRIGGER users_before_insert
    BEFORE INSERT ON users
    FOR EACH ROW
    BEGIN
      SELECT users_seq.NEXTVAL INTO :new.id FROM dual;
    END;
    /
    INSERT INTO users (username, password, email) VALUES ('john_doe', 'hashed_password', 'john.doe@example.com');
    "

    echo "$SQL_COMMANDS" | $SQLPLUS_CMD
else
    echo "The USERS table already exists or an error occurred checking its existence."
fi
