# Auto-Vacuumer

![rosie gets it](http://cyberneticzoo.com/wp-content/uploads/file/rosie-the-robot-jetsons-vacuum.jpg)


### Background

This tool uses [dbt](https://github.com/analyst-collective/dbt) for managing database credentials. It assumes you want to connect to a Redshift instance through a bastion server (specified in your `~/.ssh/config` file).

### Usage

Create a file called `prod.yml` in the `config/` directory with the desired dbt profile and cron settings. Then, run:
```bash
$ python schedule.py
```
to install the new CronTab. If your cron config changes, just run the above command again to delete existing cron jobs and install the new ones. Only cron jobs containing the comment "autovacuum scheduler" will be deleted!


### legal

Use at your own risk! 
