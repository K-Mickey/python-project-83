# Page Analyzer

### Hexlet tests and linter status:
[![Actions Status](https://github.com/K-Mickey/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/K-Mickey/python-project-83/actions)
[![Python CI](https://github.com/K-Mickey/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/K-Mickey/python-project-83/actions/workflows/pyci.yml)

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=K-Mickey_python-project-83)

## Description

This project is a web application that allows you check any site for SEO compliance.
Its finds the main page and checks the following parameters: 
- status code
- title
- h1
- description

Link: https://python-project-83-guhq.onrender.com

The project was created as part of the [Hexlet course](https://app.hexlet.io/).

## Key features

- Add new sites on the main page
- Control all sites in one place
- Move to the site to be checked
- View the details of the site

## Requirements
- UV 0.5 or higher
- PostgreSQL
- Git

## Installation

Choose a place for the clone and run the following commands:

```shell
git clone https://github.com/K-Mickey/python-project-83.git
cd python-project-83
make install
make build
```

### Virtual environment

Create `.env` file in the root directory of the project and add the following variables:
```text
# required
SECRET_KEY = "your_secret_key"
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/page_analyzer"

# optional
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

# test
TEST_BASE_DB_URL = "postgresql://postgres:postgres@localhost:5432/test_page_analyzer"
MIGRATION_SCRIPT = "database.sql"
```

## Usage

Run the following command:
```shell
make start
```

### Development

- Run server: `make dev`
- Run migrations: `make migrate`
- Run tests: `make test`
- Run linter: `make lint`
- Run tests and linter: `make check`
- Run test coverage: `make test-coverage`
