<!-- <p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://avatars1.githubusercontent.com/u/69718719?s=200&v=4" alt="Project logo"></a>
</p> -->

<h3 align="center">Database Migration Tool</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/kylelobo/The-Documentation-Compendium.svg)](https://github.com/MadeByMads/mad-migration/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/kylelobo/The-Documentation-Compendium.svg)](https://github.com/MadeByMads/mad-migration/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>


## 🧐 About <a name = "about"></a>

Database Migration Tool has been designed for those who wants migrate their data from one database to another database. Mainly tool is emphazied on migrating data from diffirent database sturctures. Currently tool chained with with mysql and porstgres drivers, we do believe to add NoSql to SQL databases and wise versa. Our main goal to make possible for all envirnments to able to migrate datas. 
## 🏁 Getting Started <a name = "getting_started"></a>

### Installing

```bash
pip install madmigration
```

## 🎈 Usage <a name="usage"></a>

After installation you should define YAML file where configuration will be taken in order to apply data to target database. Yaml file with list and dictionaries  may contain following structures:

#### Connection Config

- SourceConfig is intented to be data from source database
- DestinationConfig is intented to be transfered data to target database

![alt text](https://github.com/MadeByMads/mad-migration/blob/master/docs/img/db.jpg)

```yaml
version: 1.1
Configs:
  - SourceConfig:
       dbURI: "mysql://root:admin@127.0.0.1/oldDB"
  - DestinationConfig:
       dbURI: "mysql://root:admin@127.0.0.1/newDB"
```

```yaml
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
              primary_key: true

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

        - sourceColumn:
            name: updateddAT
          destinationColumn:
            name: updated_at

```

madmigrate -f migrate.yaml


## ✍️ Authors <a name = "authors"></a>

- [@AliyevH](https://github.com/AliyevH) - Idea & Initial work
- [@Turall](https://github.com/Turall) 
- [@sabuhish](https://github.com/sabuhish)

See also the list of [contributors](https://github.com/MadeByMads/mad-migration/graphs/contributors) who participated in this project.


## Contributing


- [Contributing](https://github.com/MadeByMads/mad-migration/blob/master/mdCONTRIBUTING.md)
