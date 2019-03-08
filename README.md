# Data Engineer Code Challenge

## General notes

As the task leaves a lot of space for assumptions and technologies to choose I have  decided to go 100% AWS for architectural decisions.
Although Google BigQuery seems to be more popular as a big data storage, I was curious to explore possibilities of Redshift. 

Other technologies from AWS I am using in this prototype can easily be replaced by similar tools from different brands with a certain ease.

Configuration of connections to AWS resources is placed in `settings.ini` 


## Events simulation

To simulate events flow I am using `generate_events.py` script which has simple settings (from `settings.ini`) to affect frequency of events generation.
   

## Events consumption
 
Script which consumes messages and stores them on a DFS `XXX` can be running either non-stop on a hosted machine (self-hosted, EC2, ElasticBeanstalk, Google AppEngine etc.)
or be a serverless solution like Lambda. A decision depends mainly on an expected load. 


## Tasks scheduling

For a hosted solution the easiest way way to support tasks scheduling is cron as it is a natural part of nearly all *nix operation systems. 
There are plenty of alternatives including cloud solutions like Cloud Scheduler from Google or AWS Batch.
I am using cron here as it is easy to replicate in any other solution. 


## Visualization

Data visualization highly depends on requirements and tools&processes which are already in use by the company. 
Tools like [Tableau](https://www.tableau.com/) are often become a choice of bigger companies, other tools like [D3](https://d3js.org/) allow in-house development of interactive graphics.
Since no specific information was given in the challenge for this part, I've decided to provide a simple visualization via matplotlib.
