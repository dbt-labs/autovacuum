#!/usr/bin/env python

from dbt.project import Project, read_profiles
from dbt.runner import RedshiftTarget
from sshtunnel import SSHTunnelForwarder
import psycopg2
import paramiko
import os, sys
import subprocess
import yaml

if len(sys.argv) != 2:
  print "Usage: {} [dbt-profile-target]".format(sys.argv[0])
  sys.exit(1)

def read_config(config_file):
  config = {}
  with open(config_file) as config_fh:
    config = yaml.load(config_fh.read())
  return config

config = read_config('config/prod.yml')

PROFILE = sys.argv[1]
BASTION_SERVER = config['bastion']

cwd = os.path.dirname(os.path.realpath(__file__))
program_name = "analyze-vacuum-schema.py"
PROG = os.path.join(cwd, program_name)
LOG_DIR = os.path.join(cwd, "logs")


if not os.path.exists(LOG_DIR):
  os.makedirs(LOG_DIR)

all_profiles = read_profiles()
p = Project({}, all_profiles, [PROFILE])
env = p.run_environment()

ssh_config = paramiko.SSHConfig()
user_config_file = os.path.expanduser("~/.ssh/config")
with open(user_config_file) as f:
    ssh_config.parse(f)
user_config = ssh_config.lookup(BASTION_SERVER)

hostname = user_config['hostname']
username = user_config['user']

def get_schemas(conn_string):
  schemas_query = "select nspname from pg_namespace where nspname not like 'pg%'"

  schemas = []
  with psycopg2.connect(conn_string) as conn:
    with conn.cursor() as cur:
      cur.execute(schemas_query)
      for result in cur.fetchall():
        schemas.append(result[0])
  return schemas

def quote(arg):
  return "'{}'".format(arg)

with SSHTunnelForwarder(hostname, ssh_username=username, remote_bind_address=(env['host'], env['port'])) as tunnel:
  local_host = "127.0.0.1"
  local_port = tunnel.local_bind_port
  print "port: ", local_port

  pg_conn_string = "dbname={} user={} password={} host={} port={} connect_timeout={}".format(
      quote(env['dbname']),
      quote(env['user']),
      quote(env['pass']),
      quote(local_host),
      local_port,
      10
  )

  schemas = get_schemas(pg_conn_string)

  for schema in schemas:
    cmd = ["python", PROG,
        "--db",      quote(env['dbname']),
        "--db-user", quote(env['user']),
        "--db-pwd",  quote(env['pass']),
        "--db-host", quote(local_host),
        "--db-port", quote(local_port),
        "--schema-name", schema,
        "--output-file", os.path.join(LOG_DIR, "log-{}.txt".format(schema))]
    print "Running analyze/vacuum for shchema: {}".format(schema)
    subprocess.check_call(cmd)

  print "done!"


