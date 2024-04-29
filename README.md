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

The Database Migration Tool was designed for those looking to migrate their data from one database to another. Additionally type casting is supported if you need to change column type in new version. Our main goal is to make data migration possible between different database servers. For example mysql, postgresql.

Currently only mysql and postgresql is supported. Future planning is to support migration from/to other databases.

---
**Documentation**: [Documentation](aliyevh.github.io/mad-migration/)
---

## 🏁 Getting Started <a name = "getting_started"></a>

### Installing

```bash
pip install madmigration
```

### Usage
```bash
madmigration -f migration_schema.yaml
```

## Configuration <a name="configuration"></a>

After installation you should define YAML file where configuration will be taken in order to apply data to target database. Yaml file with list and dictionaries may contain following structures:


![alt text](docs/img/db.jpg)

#### Connection Config

- SourceConfig is intented to be data from source database
- DestinationConfig is intented to be transfered data to target database

```yaml
version: 0.1.6
Configs:
  - SourceConfig:
       dbURI: "postgres://admin:admin@127.0.0.1/oldDB"
  - DestinationConfig:
       dbURI: "mysql://admin:admin@127.0.0.1/newDB"

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
              index: true

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
            name: updatedAT
          destinationColumn:
            name: updated_at
            options:
              type_cast: datetime

```

`Configs section`
- `SourceConfig` set the source database database configurations
  - `dbURI` source database URI 
- `DestinationConfig` set the destination database configurations
  - `dbURI` destination database URI 
```yml
Configs:
  - SourceConfig:
       dbURI: "postgres://root:admin@127.0.0.1/oldDB"  # set source database uri
  - DestinationConfig:
       dbURI: "mysql://root:admin@127.0.0.1/newDB"  # set destination database uri
```
`migrationTables section`
- `migrationTables` in this configuration, you will write the source of the table that you have to migrate and the destination tables that will migrate the data. 
  - `migrationTable` specify the source and destination table name
    - `SourceTable` information about source table
      - `name` source table name
    - `DestinationTable` information about destination table
      - `name` destination table name
      - `create` bool value. This parameter tells the program whether it should create a table or not. (`default false`)
```yml
migrationTables:
  - migrationTable:
      SourceTable:
        name: users
      DestinationTable:
        name: persons
        create: True
```
`MigrationColumns section` 
- `MigrationColumns` specify source and destination column
  - `sourceColumn`  information about source column
    - `name` source column name
  - `destinationColumn` information about destination column
    - `name` destination column name
    - `options` column options
      - `type_cast` destination column type name varchar,integer etc. (`when we convert data we use this parameter`) 

```yml
MigrationColumns:
  - sourceColumn:
      name: id
    destinationColumn:
      name: id
      options:
        type_cast: bigint
        primary_key: true
        autoincrement: true
```

**If you want to create a foreign key you can specify it in the column parameters**
```yml
- sourceColumn:
    name: USERID
  destinationColumn:
    name: user_id
    options:
      type_cast: uuid
      foreign_key:
        table_name: users
        column_name: id
        ondelete: CASCADE
```

### You can split your .yaml files or import .json file into .yaml file.
You must create the main .yaml file and importing other files into main .yaml file. 

`main.yaml` file
```yml 
version: 1.1
Configs:
  - SourceConfig:
      dbURI: "mysql://admin:admin@127.0.0.1/old"
  - DestinationConfig:
      dbURI: "postgresql://admin:admin@127.0.0.1/new"

migrationTables:
  - migrationTable: !import company.yaml
  - migrationTable: !import op_cond.json

```

`company.yaml` file
```yml
SourceTable:
  name: company
DestinationTable:
  name: company
  create: true 

MigrationColumns:
  - sourceColumn:
      name: id
    destinationColumn: 
      name: id
      options:
        primary_key: true
        type_cast: uuid

  - sourceColumn:
      name: name
    destinationColumn:
      name: name
      options:
        length: 120
        type_cast: varchar
        nullable: false

  - sourceColumn:
      name: created
    destinationColumn:
      name: created
      options:
        type_cast: datetime
  - sourceColumn:
      name: updated
    destinationColumn:
      name: updated
      options:
        type_cast: datetime
        nullable: true
```

`op_conds.json` file
```json
{
    "SourceTable": {
      "name": "operation_conditions"
    },
    "DestinationTable": {
      "name": "operation_conditions",
      "create": true
    },
    "MigrationColumns": [
      {
        "sourceColumn": {
          "name": "id"
        },
        "destinationColumn": {
          "name": "id",
          "options": {
            "primary_key": true,
            "type_cast": "uuid"
          }
        }
      },
      {
        "sourceColumn": {
          "name": "interest"
        },
        "destinationColumn": {
          "name": "interest",
          "options": {
            "type_cast": "varchar",
            "length": 30,
            "nullable": false
          }
        }
      },
      {
        "sourceColumn": {
          "name": "FIFD"
        },
        "destinationColumn": {
          "name": "FIFD",
          "options": {
            "type_cast": "varchar",
            "length": 30,
            "nullable": false
          }
        }
      },
      {
        "sourceColumn": {
          "name": "comission"
        },
        "destinationColumn": {
          "name": "comission",
          "options": {
            "type_cast": "varchar",
            "length": 30,
            "nullable": false
          }
        }
      }
    ]
  }
```

See also the list of [contributors](https://github.com/MadeByMads/mad-migration/graphs/contributors) who participated in this project.


## Contributing
We are open to  new ideas, additions. If you have any we would be happy to recieve and diccuss.

- [Contributing](https://github.com/AliyevH/mad-migration/blob/master/mdCONTRIBUTING.md)
