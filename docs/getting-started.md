## Configuration <a name="configuration"></a>

After installation you should define YAML file where configuration will be taken in order to apply data to target database. Yaml file with list and dictionaries may contain following structures:





## Example:
We have `users` database. We want to migrate it to `persons` database.

![Alt text](img/db.jpg)

## Lets create yaml file for our migration tool.

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

## `Configs section`
- `SourceConfig` set the source database configurations
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
 
## migrationTables section

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

## MigrationColumns section

- `MigrationColumns` specify source and destination column
  - `sourceColumn`  information about source column
    - `name` source column name
  - `destinationColumn` information about destination column
    - `name` destination column name
    - `options` column options
    - `type_cast` destination column type name [`varchar`, `integer`, `etc`]. When we convert data we use this parameter

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

If you want to create a foreign key you can specify it in the column parameters

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

## You can split your .yaml files
To split yaml files you must create `main.yaml` file and import other files into `main.yaml` file.
