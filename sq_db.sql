CREATE TABLE IF NOT EXISTS mainmenu (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
url text NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
id_post integer PRIMARY KEY AUTOINCREMENT,
user_id_post integer NOT NULL,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
user_id integer PRIMARY KEY AUTOINCREMENT,
login text NOT NULL,
email text NOT NULL,
psw text NOT NULL,
avatar BLOB DEFAULT NULL,
first_name text DEFAULT NULL,
last_name text DEFAULT NULL,
country text DEFAULT NULL,
city text DEFAULT NULL,
blog text DEFAULT NULL,
time integer NOT NULL
);