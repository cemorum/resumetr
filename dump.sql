CREATE TABLE Users (
  ID                SERIAL        PRIMARY KEY,
  Telegram_ID       INTEGER       NOT NULL,
  Candidate_Name    VARCHAR(50)   NOT NULL,
  Contacts          VARCHAR(150)  NOT NULL,
  About             VARCHAR(150)  NOT NULL,
  Candidate_Role    VARCHAR(50)   NOT NULL,
  Score             INTEGER       NOT NULL
);


create or replace function insert_user(
  p_tg_id integer,
  p_name varchar,
  p_contacts varchar,
  p_about varchar,
  p_role varchar,
  p_score integer
)
returns void as
$$
 begin
  insert into Users (Telegram_ID, Candidate_Name, Contacts, About, Candidate_Role, Score)
  values (p_tg_id, p_name, p_contacts, p_about, p_role, p_score);
  exception when others
  then
   raise notice 'Ошибка регистрации в бд';
  end;
$$
language plpgsql;

