## alembic commands 

1.Initialize Alembic (One Time)
------------------------------
alembic init -t generic migration

this commands will create 
migration/
    versions/
    env.py
alembic.ini
------------------------------


2. Configure the Database Connection
------------------------------------
Now, tell Alembic where your database is.

    Edit alembic.ini

Find the sqlalchemy.url line and update it to point to your Dockerized PostgreSQL:

sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/fastapi_db


    Edit migration/env.py

Make sure it imports your models:

from dbs import models

Also, set:

target_metadata = Base.metadata


3. Create the First Migration
-----------------------------
Generate the initial migration file based on your Tool and Agent models:

alembic revision --autogenerate -m "initial migration"

A new file will appear in migration/versions/ like 1234abcd_initial_migration.py.

4. Apply the Migration
------------------------
Run the migration to create the tables in your database:

alembic upgrade head

Upgrade one revision
alembic upgrade +1


Upgrade to a specific revision
alembic upgrade <revision_id>
alembic upgrade 1234abcd_initial_migration


Merge Migration Branches

alembic merge -m "merge branches" head1 head2



# Modify SQLAlchemy models

# Generate migration
alembic revision --autogenerate -m "add address column"

# Review the migration file
cat migration/versions/*.py

# Apply it
alembic upgrade head

# Verify
alembic current