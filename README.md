# The explanation

To understand how it work this script, first must explain how work Jenkins ecosystem at a very basic level. Jenkins use jobs like objects or structures created inside projects, so a folder is a job, a pipeline is a job too, a branch (git) is also a job. The only diferent are builds, that are iterations over that concatenation of jobs. An URL of Jenkins describe how jobs are nested between them to show at the end the number of the build. Lets see this url sample of Jenkins.

**https://jenkins.domain-company.com/job/Folder-FOO/job/multibranch-pipeline-BAR/job/development/3/**

So this script iterate over all jobs it is finding in a loop, asking for the configuration file (config.xml), get in folders and sub folders, until find a multibranch pipeline. When it find it, the script read the xml file, and extract the tags values and paste it in a text file, line by line, the get the report.

## How to run the script
First install the requirements

    pip install -r requirements.txt

Ill recommend to run with a > to get a txt report

    python main.py > report.txt