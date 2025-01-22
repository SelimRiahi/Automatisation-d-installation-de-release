-- Drop existing sequence and table if they exist
begin
    execute immediate 'DROP SEQUENCE users_seq';
exception
    when others then
        null; -- Ignore if sequence doesn't exist
end;

begin
    execute immediate 'DROP TABLE users';
exception
    when others then
        null; -- Ignore if table doesn't exist
end;

-- Create sequence for generating user IDs
create sequence users_seq start with 1 increment by 1 nocache nocycle;

-- Create users table
create table users (
    id       number primary key,
    username varchar2(255) not null,
    password varchar2(255) not null,
    email    varchar2(255) not null
);

-- Create trigger to automatically generate user IDs before insert
create or replace trigger users_before_insert before
    insert on users
    for each row
begin
    select users_seq.nextval
      into :new.id
      from dual;
end;
/

-- Insert single random user
declare
    v_username varchar2(255);
    v_password varchar2(255);
    v_email    varchar2(255);
begin
    v_username := 'user_'
                  || dbms_random.string(
                                       'X',
                                       6
                     ); -- Generate random username
    v_password := 'pass_'
                  || dbms_random.string(
                                       'X',
                                       6
                     ); -- Generate random password
    v_email    := v_username || '@example.com'; -- Generate random email
    insert into users (
        username,
        password,
        email
    ) values (
        v_username,
        v_password,
        v_email
    );
    commit; -- Commit the transaction
end;
/