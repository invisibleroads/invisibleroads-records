# InvisibleRoads Records

This package adds database functionality to your pyramid web service.

## Use

Install dependencies.

    pip install -U cookiecutter

Initialize project.

    cookiecutter https://github.com/invisibleroads/invisibleroads-cookiecutter

Follow the instructions in the generated README.

## Test

    git clone https://github.com/invisibleroads/invisibleroads-records
    cd invisibleroads-records
    pip install -e .[test]
    pytest --cov=invisibleroads_records --cov-report term-missing tests
