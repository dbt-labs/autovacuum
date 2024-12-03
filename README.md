# ***Archival Notice***
This repository has been archived.

As a result all of its historical issues and PRs have been closed.

Please *do not clone* this repo without understanding the risk in doing so:
- It may have unaddressed security vulnerabilities
- It may have unaddressed bugs

<details>
   <summary>Click for historical readme</summary>

# Auto-Vacuumer

![rosie gets it](http://cyberneticzoo.com/wp-content/uploads/file/rosie-the-robot-jetsons-vacuum.jpg)


### Background

This tool uses [dbt](https://github.com/analyst-collective/dbt) for managing database credentials. It assumes you want to connect to a Redshift instance through a bastion server (specified in your `~/.ssh/config` file).

### Usage

Create a file called `prod.yml` in the `config/` directory with the desired dbt profile and cron settings. Then, run:
```bash
$ python schedule.py
```
to install the new CronTab. If your cron config changes, just run the above command again to delete existing cron jobs and install the new ones. Only cron jobs containing the comment &quot;autovacuum scheduler&quot; will be deleted!


### legal

Use at your own risk! 

