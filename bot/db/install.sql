create table if not exists "user"
(
    id          serial  not null
        constraint telegram_user_pk
            primary key,
    telegram_id bigint  not null,
    is_bot      boolean not null,
    first_name  varchar,
    last_name   varchar,
    lang_code   varchar,
    phone       varchar,
    username    varchar,
    create_ts   timestamp with time zone default now()
);

create table if not exists chat
(
    id          serial                                 not null
        constraint chat_pk
            primary key,
    telegram_id bigint                                 not null,
    gigagroup   boolean                  default false not null,
    megagroup   boolean                  default true  not null,
    create_ts   timestamp with time zone default now(),
    title       varchar
);

create unique index if not exists chat_telegram_id_uindex
    on chat (telegram_id);

create unique index if not exists telegram_user_telegram_id_uindex
    on "user" (telegram_id);

create table if not exists chat_user_relation
(
    chat_id bigint
        constraint chat_user_relation_chat_id_fk
            references chat,
    user_id bigint
        constraint chat_user_relation_telegram_user_telegram_id_fk
            references "user"
);

create index if not exists chat_user_relation_chat_id_index
    on chat_user_relation (chat_id);

create unique index if not exists chat_user_relation_chat_id_user_id_uindex
    on chat_user_relation (chat_id, user_id);

create index if not exists chat_user_relation_user_id_index
    on chat_user_relation (user_id);

create table if not exists report
(
    id        serial
        constraint report_pk
            primary key,
    create_ts timestamp with time zone default now(),
    chat_id   integer not null
        constraint report_chat_id_fk
            references chat,
    user_id   integer not null
        constraint report_user_id_fk
            references "user",
    text      text    not null
);

create table if not exists chat_settings
(
    chat_id            bigint                not null
        constraint chat_settings_pk
            primary key
        constraint chat_settings_chat_id_fk
            references chat,
    notice_msg         text    default 'Hi everyone, time to daily meeting 💪'::text,
    congratulation_msg text    default 'Good job, guys!'::text,
    censure_msg        text    default '{}, you are missing ours daily 😞'::text,
    monday             boolean default true not null,
    tuesday            boolean default false  not null,
    wednesday          boolean default false not null,
    thursday           boolean default false not null,
    friday             boolean default false not null,
    saturday           boolean default false not null,
    sunday             boolean default false not null
);

create table notice_log
(
    day         smallint not null,
    chat_id     bigint   not null
        constraint notice_log_chat_id_fk
            references chat,
    notice_type varchar  not null,
    created     timestamp with time zone default now()
);

create index notice_log_day_chat_id_notice_type_index
    on notice_log (day, chat_id, notice_type);

create table meeting
(
    chat_id  bigint                                 not null
        constraint meeting_chat_id_fk
            references chat,
    users    integer[],
    start_ts timestamp with time zone default now() not null
);


create index meeting_chat_id_start_ts_index
    on meeting (chat_id, start_ts);
