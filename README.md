<p align="center">
  <a href="" rel="noopener">
 <img width=400px height=400px src="https://github.com/MadeByMads/mad-migration/blob/master/docs/img/mm.jpg" alt="Project logo"></a>
</p>

<h3 align="center">Database Migration Tool</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/MadeByMads/mad-migration/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/MadeByMads/mad-migration/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>


## 🧐 About <a name = "about"></a>

The Database Migration Tool was designed for those looking to migrate their data from one database to another. Basically, the tool is focused on transferring data from different database structures. Currently, the MySQL and Postgres driver related tool allows us to add NoSQL to SQL databases and vice versa. Our main goal is to make data migration possible in all environments.


---
**Documentation**: [Documentation](https://madebymads.github.io/mad-migration/)
---

## 🏁 Getting Started <a name = "getting_started"></a>

### Installing

```bash
pip install madmigration
```

## 🎈 Usage <a name="usage"></a>

After installation you should define YAML file where configuration will be taken in order to apply data to target database. Yaml file with list and dictionaries  may contain following structures:


![alt text](https://github.com/MadeByMads/mad-migration/blob/master/docs/img/db.jpg)

#### Connection Config

- SourceConfig is intented to be data from source database
- DestinationConfig is intented to be transfered data to target database

```yaml
version: 1.1
Configs:
  - SourceConfig:
       dbURI: "postgres://root:admin@127.0.0.1/oldDB"
  - DestinationConfig:
       dbURI: "mysql://root:admin@127.0.0.1/newDB"

migrationTables:
  - migrationTable:
      SourceTable:
        name: users
      DestinationTable:
        name: persons
        create: True

      MigrationColumns:
        - sourceColumn:
            name: id
          destinationColumn:
            name: id
            options:
              type_cast: bigint
              primary_key: true
              autoincrement: true

        - sourceColumn:
            name: name
          destinationColumn:
            name: fname
            options:
              type_cast: varchar
              length: 32
      
        - sourceColumn:
            name: surname
          destinationColumn:
            name: lname
            options:
              type_cast: varchar
              length: 32

        - sourceColumn:
            name: age
          destinationColumn:
            name: age
            options:
              type_cast: int

        - sourceColumn:
            name: createdAT
          destinationColumn:
            name: created_at
            options:
              type_cast: datetime

        - sourceColumn:
            name: updateddAT
          destinationColumn:
            name: updated_at
            options:
              type_cast: datetime

```

- DestinationConfig - set the destination database, if the specified database does not exist we will create it.
- migrationTables - under this config, you will write the source of the table that you should migrate and the destination tables that will migrate the data.
  - migrationTable - specify the source and destination table name
    - MigrationColumns - specify source and destination column

### We will create all tables and database on the destination server if they do not exist

madmigrate -f migration_schema.yaml


## ✍️ Authors <a name = "authors"></a>

- [@AliyevH](https://github.com/AliyevH) - Idea & Initial work
- [@Turall](https://github.com/Turall) 
- [@sabuhish](https://github.com/sabuhish)

See also the list of [contributors](https://github.com/MadeByMads/mad-migration/graphs/contributors) who participated in this project.


## Contributing


- [Contributing](https://github.com/MadeByMads/mad-migration/blob/master/mdCONTRIBUTING.md)
