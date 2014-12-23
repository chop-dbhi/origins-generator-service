# Origins Generator Service

[![Build Status](https://travis-ci.org/chop-dbhi/origins-generator-service.svg?branch=master)](https://travis-ci.org/chop-dbhi/origins-generator-service) [![Coverage Status](https://img.shields.io/coveralls/chop-dbhi/origins-generator-service.svg)](https://coveralls.io/r/chop-dbhi/origins-generator-service)

The Origins Generator Service exposes an HTTP service for generating provenance data in the PROV-JSON format which is directly consumable by [Origins](https://github.com/chop-dbhi/origins/).

## Install

Docker image (recommended). All generator dependencies are included.

```
docker run -p 5000:5000 bruth/origins-generator-service
```

Manual. Generator dependencies need to be installed manually.

```
pip install origins-generators
```

### Optional Dependencies

- `psycopg2`
- `pymysql`
- `Oracle-CX`
- `pymongo`
- `PyVCF`
- `PyMongo`
- `OpenPyXL`

## Supported Sources

- Relational Databases
    - PostgreSQL
    - MySQL
    - SQLite
    - Oracle
- Document Stores
    - Mongodb
- Delimited Files
    - CSV, TSV (any delimited)
- Data Dictionaries
    - Column-based attributes
- Microsoft Excel
- File System
- Variant Call Format (VCF) Files
- REDCap (MySQL)
- REDCap (REST API)
- REDCap (CSV)
- Harvest (REST API)
- GitHub Issues
- Git

## Interface

**`GET /`**
    
Return a list of available sources.

```bash
$ curl http://localhost:5000
[{
    "name": "postgresql",
    "description": "Generator for PostgreSQL databases.",
    "links": {
        "self": "http://localhost:5000/postgresql/",
    },

    ...
}]

```

**`GET /<source>/`**
    
Return a description information and the POST options for generating a *resource* from a source. The output is in the [JSON Schema](http://json-schema.org/) format.

```bash
$ curl http://localhost:5000/postgresql/
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "postgresql",
    "description": "Generator for PostgreSQL databases.",
    "required": ["database"],
    "properties": {
        "database": {
            "description": "The name of the database."
            "type": "string",
        },
        "host": {
            "description": "The hostname of the server.",
            "type": "string",
            "default": "locahost",
        },
        "port": {
            "description": "The port of the server.",
            "type": "integer",
            "default": 5432,
        },

        ...
    }
}
```

**`POST /<source>/`**
    
Generates a export from the source.

```bash
$ curl -X POST -H 'Content-Type: application/json' http://localhost:5000/postgresql/ -d '
{
    "database": "chinook",
    "host": "213.48.19.100",
    "port": 5432,
    "user": "nobody",
    "password": "nothing"
}'
```

The response will be in the PROV-JSON format which can be imported directly into Origins.
