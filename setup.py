import os, sys
from setuptools import setup, find_packages

import audit_log
from audit_log import VERSION, __version__

if VERSION[-1] == "final":
    STATUS = ["Development Status :: 5 - Production/Stable"]
elif "beta" in VERSION[-1]:
    STATUS = ["Development Status :: 4 - Beta"]
else:
    STATUS = ["Development Status :: 3 - Alpha"]


def get_readme():
    try:
        return open(os.path.join(os.path.dirname(__file__), "README.rst")).read()
    except IOError:
        return ""


setup(
    name="django-audit-log2",
    version=__version__,
    packages=find_packages(exclude=["testproject"]),
    author="Wenjun Kang",
    author_email="wkang0@uchicago.edu",
    license="New BSD License (http://www.opensource.org/licenses/bsd-license.php)",
    description="Audit trail for django models",
    long_description=get_readme(),
    url="https://github.com/wkang0/django-audit-log2",
    download_url="https://github.com/wkang0/django-audit-log2/releases",
    include_package_data=True,
    zip_safe=False,
    classifiers=STATUS
    + [
        "Environment :: Plugins",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
