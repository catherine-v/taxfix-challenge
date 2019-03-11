from configparser import ConfigParser
from datetime import datetime
import logging

import pandas as pd
import psycopg2


logging.basicConfig(level=logging.INFO)

REDSHIFT_DSN_STR = "dbname={database} user={user} password={password} host={host} port={port}"
DEFAULT_SETTINGS = {
    "user": "user",
    "password": "password",
    "host": "redshift.host",
    "port": "5439",
    "database": "events",
    "report_events": "submission_success,registration_initiated"
}


def load_settings() -> dict:
    """
    Loads settings from file

    :return: dictionary with settings key-value pairs
    """
    config = ConfigParser()
    config.read("settings.ini")
    return {
        "user": config.get("redshift", "user", fallback=DEFAULT_SETTINGS["user"]),
        "password": config.get("redshift", "password", fallback=DEFAULT_SETTINGS["password"]),
        "host": config.get("redshift", "host", fallback=DEFAULT_SETTINGS["host"]),
        "port": config.get("redshift", "port", fallback=DEFAULT_SETTINGS["port"]),
        "database": config.get("redshift", "database", fallback=DEFAULT_SETTINGS["database"]),
        "report_events": config.get("events", "report_events", fallback=DEFAULT_SETTINGS["report_events"]),
    }


if __name__ == "__main__":
    settings = load_settings()
    dt = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

    # Connect to Redshift
    with psycopg2.connect(REDSHIFT_DSN_STR.format(**settings)) as conn:
        with conn.cursor() as cursor:
            for event in settings["report_events"].split(","):
                cursor.execute("""
                    SELECT TO_CHAR(DATE_TRUNC('day', timestamp), 'YYYY-MM-DD') as date,
                           context_device_type,
                           COUNT(*) as cnt
                    FROM events
                    WHERE event = %s
                    GROUP BY DATE_TRUNC('day', timestamp), context_device_type
                """, (event, ))

                # Transform data for plotting
                results = pd.DataFrame(cursor.fetchall(), columns=["date", "platform", "count"])
                results.set_index("date", inplace=True)
                results.sort_index(inplace=True)
                data = results.pivot(columns="platform", values="count")

                # Create a graph and save it
                graph = data.plot.bar()
                graph.get_figure().savefig(f"{event}-{dt}.png")
