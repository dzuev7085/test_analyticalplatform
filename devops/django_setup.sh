#!/bin/sh

cd ../ncr_website

# Migrate Django db changes
python3 manage.py migrate --noinput # > /var/log/deploy_migration.log

# Collect static
if [ "$ENVIRONMENT_MODE" = "PROD" ] || [ "$ENVIRONMENT_MODE" = "UAT" ]
then
    python3 manage.py collectstatic --noinput # > /tmp/ncr/deploy_static.log
fi

# Load fixtures data
python3 manage.py loaddata config/fixtures/*.json # &>> /tmp/ncr/deploy_fixture.log

# Create an admin user
python3 manage.py setup_superuser # > /tmp/ncr/deploy.log

# Some things should be run in the dev environments
if [ "$ENVIRONMENT_MODE" = "DEV" ] || [ "$ENVIRONMENT_MODE" = "UAT" ]
then

    # Create some test users
    python3 manage.py uat_users # > /tmp/ncr/deploy_uat.log

    # Create some test issuers
    python3 manage.py uat_issuer_setup # > /tmp/ncr/deploy_uat.log

fi

# Some things should be setup in production and UAT
if [ "$ENVIRONMENT_MODE" = "PROD" ] || [ "$ENVIRONMENT_MODE" = "UAT" ]
then

    python3 manage.py prod_users

fi
