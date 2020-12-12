from setuptools import setup, find_packages
import madmigration

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="madmigration",
    packages=find_packages(),
    version="0.1.1",
    entry_points="""
        [console_scripts]
        madmigrate=madmigration.scripts.commands:cli
    """,
    author="Hasan Aliyev, Tural Muradov, Sabuhi Shukurov",
    author_email="hasan.aliyev.555@gmail.com, tural_m@hotmail.com, sabuhi.shukurov@gmail.com",
    license='MIT',
    description="Mad migration",
    long_description_content_type="text/markdown",
    url="https://github.com/MadeByMads/mad-migration",
    long_description=long_description,
    install_requires=["click>=7.1.2","SQLAlchemy>=1.3.18","mysqlclient>=2.0.1","psycopg2>=2.8.5","alembic>=1.4.2", "PyYAML>=5.3.1 "],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_packge_data=True,
    tests_require=[
        'pytest',
        'mock',
    ],
    platforms=['any'],
    python_requires='>=3.6',
    project_urls={  
        'Bug Reports': 'https://github.com/MadeByMads/mad-migration/issues',
        'Say Thanks!': 'https://github.com/MadeByMads/mad-migration/network/dependencies',
        'Source': 'https://github.com/MadeByMads/mad-migration',
    },
)



