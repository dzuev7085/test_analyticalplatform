#!/bin/sh
# Script to run the Django test suite

if [ -z != $1 ] ; then
    apps=$1
else
    apps="rating_process issuer issue gui integrations user_profile rating credit_assessment"
fi

# Inform user what we are testing
echo "Running tests for $apps"

# Running Django's test suite in parallel-mode seems to break coverage
cd ../ && coverage run --source='.' ncr_website/manage.py test $apps

# Filter out 100% until we have reached a decent percentage
#if [ -z != $1 ] ; then
#    echo ""
#else
#    coverage report -m | grep -v 100%
#fi
