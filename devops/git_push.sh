#!/bin/sh

cd ..

find -name '*.py' -not -path "./.tox/*" -not -path "./venv/*" -not -path "./*/__docs/*" -not -path "./*/tests/*" -not -path "./*/migrations/*" -not -path "./*/dev_uat_tools/*" | xargs flake8 | tee devops/flake8.log
RESULT=$?

if [ $RESULT -eq 0 ]; then
    more devops/flake8.log
    git push
else
    more devops/flake8.log
fi
