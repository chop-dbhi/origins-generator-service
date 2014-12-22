# Origins Generators

An Origins generator extracts structural and descriptive metadata from common data sources into the PROV-JSON format which is directly consumable by [Origins](https://github.com/cbmi/origins/).

All generators are exposed through an HTTP service. Performing a GET to the root endpoint will return a set available generators and options each generator supports.

## Install

Docker image (recommended). All generator dependencies are included.

```
docker run --publish 5000:5000 bruth/origins-generators
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

## REST Interface

**`GET /`**
    
Return a list of supported sources.

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


## Sources

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
