CREATE TABLE offer_channels(
    category_id VARCHAR(64) NOT NULL,
    channel_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) PRIMARY KEY,
    header_role_id VARCHAR(64) NOT NULL
);

CREATE TABLE users_channels(
    offer_message_id VARCHAR(64) NOT NULL REFERENCES offer_channels(message_id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL,
    channel_id VARCHAR(64) NOT NULL,

    CONSTRAINT users_channels_uq UNIQUE(offer_message_id, user_id, channel_id)
);

CREATE TABLE give_role_channels(
    channel_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) PRIMARY KEY
);

CREATE TABLE give_roles(
    give_role_message_id VARCHAR(64) REFERENCES give_role_channels(message_id) ON DELETE CASCADE,
    button_id VARCHAR(32) NOT NULL,
    role_id VARCHAR(64) NOT NULL
);

CREATE TABLE given_user_roles(
    give_role_message_id VARCHAR(64) REFERENCES give_role_channels(message_id) ON DELETE CASCADE NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    give_time DATE NOT NULL,

    CONSTRAINT given_user_roles_uq UNIQUE(give_role_message_id, user_id)
);

CREATE TABLE polls(
    channel_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) PRIMARY KEY,
    timeout TIME 
);

CREATE TABLE polls_votes(
    message_id VARCHAR(64) REFERENCES polls(message_id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL,
    vote_index INT NOT NULL
);

CREATE TABLE config(
    embed_color VARCHAR(32)
);
INSERT INTO config VALUES('');
