
'''
telegram_user:
    id serial
    telegram_id  bigint
    bot  bool
    first_name varchar
    last_name  varchar
    lang_code  varchar
    phone      varchar
    username   varchar
    create_ts timestamptz

telegram_chat:
    id serial
    chat_id bigint
    gigagroup bool
    megagroup bool
    create_ts timestamptz

report:
    chat_id foreign key(chat_id)
    message text
    telegram_user_id foreign key(telegram_user)
    create_ts timestamptz
'''