from configparser import ConfigParser
import logging

import boto3
import psycopg2


logging.basicConfig(level=logging.INFO)

REDSHIFT_DSN_STR = "dbname={database} user={user} password={password} host={host} port={port}"
DEFAULT_SETTINGS = {
    "user": "user",
    "password": "password",
    "host": "redshift.host",
    "port": "5439",
    "database": "events",
    "arn_credentials": "arn:aws:iam::0123456789012:role/MyRedshiftRole",
    "s3_bucket": "some-bucket",
}


def load_settings() -> dict:
    """
    Loads settings from file

    :return: dictionary with settings key-value pairs
    """
    config = ConfigParser()
    config.read("settings.ini")
    return {
        "s3_bucket": config.get("aws", "s3_bucket", fallback=DEFAULT_SETTINGS["s3_bucket"]),
        "user": config.get("redshift", "user", fallback=DEFAULT_SETTINGS["user"]),
        "password": config.get("redshift", "password", fallback=DEFAULT_SETTINGS["password"]),
        "host": config.get("redshift", "host", fallback=DEFAULT_SETTINGS["host"]),
        "port": config.get("redshift", "port", fallback=DEFAULT_SETTINGS["port"]),
        "arn_credentials": config.get("redshift", "arn_credentials", fallback=DEFAULT_SETTINGS["arn_credentials"]),
        "database": config.get("redshift", "user", fallback=DEFAULT_SETTINGS["database"]),
    }


if __name__ == "__main__":
    settings = load_settings()

    # Get list of files available for the u pload
    s3 = boto3.client("s3")
    res = s3.list_objects(Bucket=settings["s3_bucket"])
    files = [f["Key"] for f in res["Contents"]]

    # Connect to Redshift
    conn = psycopg2.connect(REDSHIFT_DSN_STR.format(**settings))
    with conn.cursor() as cursor:
        for file in files:
            cursor.execute("""
                COPY events
                FROM 's3://{bucket}/{key}'
                IAM_ROLE '{arn}'
                JSON 'auto'
                TIMEFORMAT 'auto';
            """.format(bucket=settings["s3_bucket"],
                       key=file,
                       arn=settings["arn_credentials"]))

            # Remove file after an upload
            s3.delete_object(Bucket=settings["s3_bucket"], Key=file)
            logging.info("Uploaded %s contents to Redshift", file)

    conn.close()

