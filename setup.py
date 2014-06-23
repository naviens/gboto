__author__ = 'naveen'
from setuptools import setup

setup(
    name="gboto",
    packages = ['gboto'],
    version="0.1",
    description="boto library for Google Compute Engine",
    author="Naveen Subramani",
    author_email="naviensubramani@gmail.com",
    url="https://github.com/naviens/gboto",
    download_url="https://github.com/naviens/gboto/archive/0.1.tar.gz",
    install_requires=[
        "oauth2client",
        "google-api-python-client",
        "python-gflags",
    ],
    license="Apache 2.0",
    keywords = ['gce', 'boto', 'google-cloud'], # arbitrary keywords
    classifiers = [],
)