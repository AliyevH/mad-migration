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


## 📝 Table of Contents

- [About](https://github.com/MadeByMads/mad-migration#-about-)
- [Getting Started](https://github.com/MadeByMads/mad-migration#-getting_started-)
- [Usage](https://github.com/MadeByMads/mad-migration#-usage-)
- [TODO](https://github.com/MadeByMads/mad-migration/projects/1)
- [Contributing](https://github.com/MadeByMads/mad-migration/blob/master/mdCONTRIBUTING.md)
- [Authors](https://github.com/MadeByMads/mad-migration#%EF%B8%8F-authors-)

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

```yaml
version: 1.1
Configs:
  - SourceConfig:
      dbURI:  "postgres://YourUserName:YourPassword@YourHostname:5432/SourDB";
  - DestinationConfig:
      dbURI:  "postgres://YourUserName:YourPassword@YourHostname:5432/DestinationDB";
```

#### Tables Config
- migrationTables list of tables to addded migration
- migrationTable dictionary 
- SourceTable
- name
- DestinationTable
- MigrationColumns
- sourceColumn
- options
- 
- 
- 

```yaml
migrationTables:
  - migrationTable:
      SourceTable:
        name: example
      DestinationTable:
        name: newtable
        create: True # -> I suggest that we have to define this option that will tell us whether we have to create tables or not

      MigrationColumns:
        - sourceColumn:
            name: id
          destinationColumn: 
            name: ID
            options:
              primary_key: true
              # autoincrement: true
              type_cast: uuid

        - sourceColumn:
            name: name
          destinationColumn:
            name: firstname
            options:
              length: 120
              type_cast: varchar

        - sourceColumn:
            name: email
          destinationColumn:
            name: EMAIL
            options:
              type_cast: varchar
              length: 120

```

madmigrate -f migrate.yaml


## ✍️ Authors <a name = "authors"></a>

- [@AliyevH](https://github.com/AliyevH) - Idea & Initial work
- [@Turall](https://github.com/Turall) 
- [@sabuhish](https://github.com/sabuhish)

See also the list of [contributors](https://github.com/MadeByMads/mad-migration/graphs/contributors) who participated in this project.

