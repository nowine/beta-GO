#!flask/bin/python

import imp
from migrate.versioning import api
from app import db
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

# Get current version and construct the migration script file name
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migrate.py' % (v + 1))

# Dynamic create an empty module for import
# (Todo: imp.new_module is deprecated, try to refactor it with
#  types.ModuleType class)
tmp_module = imp.new_module('old_model')

# Based on dababase to create current DB model source code
old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# Run the old_model scripts in the tmp_module dictionary
exec(old_model, tmp_module.__dict__)

# Generate DB update scripts and stored in migration file
scripts = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
open(migration, 'wt').write(scripts)

# Upgrade DB version
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('The migration script is stored as ' + migration)
print('The current version: %03d' % (v,))
