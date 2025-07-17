from setuptools import find_packages
from setuptools import setup


version = "2.0.0a1.dev0"

long_description = (
    open("README.rst").read() + "\n" + "Contributors\n"
    "============\n"
    + "\n"
    + open("CONTRIBUTORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
    + "\n"
)

setup(
    name="dexterity.localroles",
    version=version,
    description="Define local roles settings by dexterity type",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.1",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="Plone Python",
    author="IMIO",
    author_email="support@imio.be",
    url="https://github.com/collective/dexterity.localroles",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/dexterity.localroles",
        "Source": "https://github.com/collective/dexterity.localroles",
        # "Tracker": (
        #     "https://github.com/collective/dexterity.localroles/issues"
        # ),
    },
    license="gpl",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=[
        "dexterity",
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Plone",
        "plone.api",
        "borg.localrole",
        "collective.z3cform.datagridfield",
        "plone.app.dexterity",
        "setuptools",
        "imio.helpers",
    ],
    extras_require={
        "test": [
            "plone.app.robotframework",
            "plone.app.testing",
            "ecreall.helpers.testing",
            "robotsuite",
        ]
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
