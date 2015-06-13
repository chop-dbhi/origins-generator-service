# Contribution Guide

- Find or create an issue on the repository addressing the change being made
- Fork the repository and create a branch

# Checklist

- The scope of each commit should be small so the impact of the change is clear.
- The commit summary should state the change and the message should be descriptive enough so a human readable CHANGELOG can be easily produced from the text.
- Sign off on all commits

# Docker for Development

## MySQL

Start the container.

```
docker run --name mysql -e MYSQL_ROOT_PASSWORD=root -p 3306 mysql
```

Create the database.

```
docker exec -it mysql mysql --user=root --password=root < tests/input/chinook_mysql.sql > /dev/null
```

## PostgreSQL

Start the container.

```
docker run --name postgres -e POSTGRES_PASSWORD=root -p 5432 postgres
```

Create the database.

```
docker exec -it postgres psql -U postgres -d chinook -c 'create database chinook'
docker exec -it postgres psql -U postgres chinook < tests/input/chinook_postgresql.sql
```

## MongoDB


Start the container with a mount to the test data. *Note: an explicit command is passed to alleviate an issue of journal files not having enough space when the daemon starts up for boot2docker users.*

```
docker run --name mongodb -p 27017 -v $PWD/tests/input/mongodb:/data mongo mongod --smallfiles
```

Create the database.

```
docker exec -it mongodb mongorestore --db chinook /data
```

## Oracle

Start the container.

```
docker run --name oracle -p 1521 wnameless/oracle-xe-11g
```

Create the database.

```
docker exec -it oracle sqlplus system/oracle@xe < tests/input/chinook_oracle.sql
```
