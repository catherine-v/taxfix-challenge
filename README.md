# Data Engineer Code Challenge

## General notes

As the task leaves a lot of space for assumptions and technologies to choose I have  decided to go 100% AWS for architectural decisions.
Although Google BigQuery seems to be more popular as a big data storage, I was curious to explore possibilities of Redshift. 

Other technologies from AWS I am using in this prototype can easily be replaced by similar tools from different brands with a certain ease.

Configuration of connections to AWS resources is placed in `settings.ini`. 
In order to connect to AWS resources I am using `boto3` library which is getting access key and secret from `$HOME/.aws/` folder or 
from environment variables.


## Events simulation

To simulate events flow I am using `generate_events.py` script which has simple settings (from `settings.ini`) to affect frequency of events generation.
Amazon SQS is being used here as an events bus. The generation script assumes the queue already exists.
   

## Events consumption
 
Script which consumes messages and stores them on a DFS `consume_events.py` can be running 
* non-stop on a hosted machine (self-hosted, EC2, ElasticBeanstalk, Google AppEngine etc.) -- in this case 
  [long polling](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-long-polling.html) is possible. 
  Such scripts can also run in parallel on several hosts or as several processes on the same machine. 
* be a serverless solution like Lambda 

A decision depends mainly on an expected load. In this implementation I am using a self-hosted script with a configurable 
long polling. 


## Tasks scheduling

For a hosted solution the easiest way way to support tasks scheduling is cron as it is a natural part of nearly all *nix operation systems. 
There are plenty of alternatives including cloud solutions like Cloud Scheduler from Google, AWS Batch or CloudWatch.
I am using cron here as it is easy to replicate in any other solution. 


## Upload into DataWarehouse

Disclaimer: I could not fully test this part of the task as I don't have access to a real Redshift cluster. 

As Redshift is based on PostgreSQL and is compatible with it's connection drivers, I'm using psycopg2 here.
`COPY` command is a recommended way to upload bulk data into Redshift.

An assumed table structure can be found in `create_table.sql`. Columns marked as `NOT NULL` are either necessary to
fulfill the task needs or a logical assumption. `VARCHAR` length are also an assumtion based on example data.

To keep scheduling flexible the script `upload_data.py` is fetching all available files from S3, uploads them to Redshift
and removes from S3 so the next job will not upload the same data causing unnecessary duplication. In a real project
it might be beneficial not to remove data from S3, but keep uploaded files in a separate bucket.
 


## Visualization

Data visualization highly depends on requirements and tools&processes which are already in use by the company. 
Tools like [Tableau](https://www.tableau.com/) are often become a choice of bigger companies, other tools like [D3](https://d3js.org/) allow in-house development of interactive graphics.
Since no specific information was given in the challenge for this part, I've decided to provide a simple visualization via matplotlib.
