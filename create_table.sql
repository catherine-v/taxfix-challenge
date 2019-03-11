CREATE TABLE events
(
  id                                 VARCHAR(36) NOT NULL,
  anonymous_id                       VARCHAR(36) NOT NULL,
  user_id                            INTEGER,
  context_app_version                VARCHAR(8),
  context_device_ad_tracking_enabled BOOLEAN,
  context_device_manufacturer        VARCHAR(32),
  context_device_model               VARCHAR(32),
  context_device_type                VARCHAR(16) NOT NULL,
  context_library_name               VARCHAR(16),
  context_library_version            VARCHAR(8),
  context_locale                     VARCHAR(5),
  context_network_wifi               BOOLEAN,
  context_os_name                    VARCHAR(32),
  context_network_carrier            VARCHAR(16),
  context_timezone                   VARCHAR(16),
  context_traits_taxfix_language     VARCHAR(5),
  event                              VARCHAR(32) NOT NULL,
  event_text                         VARCHAR(64) NOT NULL,
  original_timestamp                 TIMESTAMPTZ,
  timestamp                          TIMESTAMP   NOT NULL SORTKEY,
  sent_at                            TIMESTAMP   NOT NULL,
  received_at                        TIMESTAMP   NOT NULL
);


