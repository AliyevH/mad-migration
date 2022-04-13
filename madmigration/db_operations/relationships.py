""""
Build relationships between tables using graph datastructure and create via bfs

Firstly it runs through the entirety of the yaml file and locates all point relationship is indicated
then it starts by creating the least dependent table and backtracks from there.

indicate the relationships per table in yaml file. compatible with mongodb


Types of Relationships
- NoSql Array to SQL Table(new table) with relationship
- relationship to relationhip(SQL and NoSQL)
- NoSQl Array to NoSQL document with Relationship(pointer to initial table)
"""


class BuildRelationship:
    pass