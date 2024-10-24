import os

import setuptools

PROJECT_NAME = "Data Science Pipeline and API server"
PROJECT_DESCRIPTION = " create a data exploration Pipeline with Flask API server"
PROJECT_URL = ""
VERSION = "1.0.0"
AUTHOR_USER_NAME = "Abderrazak Chahid"
AUTHOR_EMAIL = "abderrazak.chahid@gmail.com"


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name=PROJECT_NAME,
    version=VERSION,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description=(PROJECT_DESCRIPTION),
    long_description=read("README.md"),
    license="BSD",
    url=PROJECT_URL,
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)


# classifiers:
# Development Status:: 1 - Planning
# Development Status:: 2 - Pre-Alpha
# Development Status:: 3 - Alpha
# Development Status:: 4 - Beta
# Development Status:: 5 - Production/Stable
# Development Status:: 6 - Mature
# Development Status:: 7 - Inactive
