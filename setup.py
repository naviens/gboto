__author__ = 'naveen'
from setuptools import setup

setup(
    name="oneclick",
    version="1.0",
    description = "OneClick Installation for Hadoop",
    author = "Naveen Subramani",
    author_email = "naviensubramani@gmail.com",
    install_requires=[
        "oauth2client",
        "google-api-python-client",
        "python-gflags",
    ],
    # ...
)