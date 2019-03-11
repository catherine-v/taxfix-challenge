from configparser import ConfigParser
import logging

import boto3
import psycopg2


logging.basicConfig(level=logging.INFO)

REDSHIFT_DSN_STR = "dbname={database} user={user} password={password} host={host} port={port}"


def load_settings() -> dict:
    """
    Loads settings from file

    :return: dictionary with settings key-value pairs
    """
    config = ConfigParser()
    config.read("settings.ini")
    return {
        "aws_access_key_id": config.get("aws", "aws_access_key_id"),
        "aws_secret_access_key": config.get("aws", "aws_secret_access_key"),
        "region": config.get("aws", "region"),
        "s3_bucket": config.get("aws", "s3_bucket"),
        "user": config.get("redshift", "user"),
        "password": config.get("redshift", "password"),
        "host": config.get("redshift", "host"),
        "port": config.get("redshift", "port"),
        "database": config.get("redshift", "database"),
        "arn_credentials": config.get("redshift", "arn_credentials"),
    }


if __name__ == "__main__":
    settings = load_settings()

    # Get list of files available for the u pload
    s3 = boto3.client("s3",
                      region_name=settings["region"],
                      aws_access_key_id=settings["aws_access_key_id"],
                      aws_secret_access_key=settings["aws_secret_access_key"])
    res = s3.list_objects(Bucket=settings["s3_bucket"])
    files = [f["Key"] for f in res["Contents"]]

    # Connect to Redshift
    with psycopg2.connect(REDSHIFT_DSN_STR.format(**settings)) as conn:
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
