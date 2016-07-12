
import yaml
from crontab import CronTab
import subprocess, os

IDENTIFER_COMMENT = "autovacuum scheduler"

def delete_configs(cron):
  "deletes existing crontab entries"

  entries = list(cron.find_comment(IDENTIFER_COMMENT))
  existing = len(entries)
  for entry in entries:
    entry.delete()
  print "Deleted {} existing cron jobs".format(existing)

def install_config(cron, cmd, name, day, hour):
  job = cron.new(command=cmd, comment=IDENTIFER_COMMENT)
  # only run it on the first minute of the hour!
  job.minute.on(0)
  job.dow.on(day)
  job.hour.on(hour)

  if not job.is_valid():
    print "ERROR: Invalid Job for {name} [disabling entry]".format(name)
    job.enable(False)
    return False
  return True

def read_config(config_file):
  config = {}
  with open(config_file) as config_fh:
    config = yaml.load(config_fh.read())
  return config

def diagnostic(installed, total):
  print "Installed {} of {} cron entries".format(installed, total)
  print "-" * 40
  subprocess.call(['crontab', '-l'])

def install(config_file):

  cwd = os.path.dirname(os.path.realpath(__file__))
  program_name = "main.py"
  script_path = os.path.join(cwd, program_name)

  config = read_config(config_file)

  clients = config['clients']

  user_cron = CronTab(user=True)
  delete_configs(user_cron)
  print 

  installed = 0
  for client in clients:
    name, profile = client['name'], client['profile']

    print "Installing cronjob for {}".format(name)
    cmd = "python '{script}' '{profile}'".format(script=script_path, profile=profile)
    if install_config(user_cron, cmd, name, client['day'], client['hour']):
      installed += 1

  user_cron.write()

  diagnostic(installed, len(clients))

if __name__ == '__main__':
  install("config/prod.yml")
