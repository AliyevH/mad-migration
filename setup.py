from setuptools import setup, find_packages

setup(
    name="madmigration",
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        madmigrate=madmigration.scripts.commands:cli
    """,
    install_requires=["click"],
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
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.* '
)


def x():
    x = []
    for i in range(10):
        x.append(i)

