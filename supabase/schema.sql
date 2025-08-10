create table if not exists assets (
    id serial primary key,
    symbol text unique
);
