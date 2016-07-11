#!/usr/bin/env python

BASTION_SERVER = 'fishtown-bastion'
QUERY = 'select now()'

from dbt.project import Project, read_profiles
from dbt.runner import RedshiftTarget

all_profiles = read_profiles()
p = Project({}, all_profiles, ['uservoice'])
env = p.run_environment()

print env

from sshtunnel import SSHTunnelForwarder
import paramiko
import psycopg2
import os

ssh_config = paramiko.SSHConfig()
user_config_file = os.path.expanduser("~/.ssh/config")
with open(user_config_file) as f:
    ssh_config.parse(f)
user_config = ssh_config.lookup(BASTION_SERVER)

hostname = user_config['hostname']
username = user_config['user']

with SSHTunnelForwarder(hostname, ssh_username=username, remote_bind_address=(env['host'], env['port'])) as tunnel:
  local_host = "127.0.0.1"
  local_port = tunnel.local_bind_port

  print "port: ", local_port

  conn_string = "dbname={} user={} password='{}' host={} port={} connect_timeout={}".format(
      env['dbname'],
      env['user'],
      env['pass'],
      local_host,
      local_port,
      10
  )

  print conn_string

  print "creating conn"
  conn = psycopg2.connect(conn_string)

  print "creating cursor"
  cur = conn.cursor()

  print "running query"
  cur.execute(QUERY)

  print "getting results!"
  print cur.fetchone()

  print "closing cursor"
  cur.close()

  print "closing conn"
  conn.close()

  print "done!"
