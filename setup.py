__author__ = 'naveen'
from setuptools import setup

setup(
    name="gce_boto",
    version="0.1",
    description="boto library for Google Compute Engine",
    author="Naveen Subramani",
    author_email="naviensubramani@gmail.com",
    install_requires=[
        "oauth2client",
        "google-api-python-client",
        "python-gflags",
    ],
    # ...
)