__author__ = 'naveen'
from setuptools import setup

setup(
    name="goto",
    packages = ['goto'],
    version="0.1",
    description="goto library for Google Compute Engine",
    author="Naveen Subramani",
    author_email="naviensubramani@gmail.com",
    url="https://github.com/naviens/goto",
    download_url="https://github.com/naviens/goto/archive/0.1.tar.gz",
    install_requires=[
        "oauth2client",
        "google-api-python-client",
        "python-gflags",
    ],
    license="Apache 2.0",
    keywords = ['gce', 'boto', 'google-cloud', 'goto'], # arbitrary keywords
    classifiers = [],
)