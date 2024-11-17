from pathlib import Path
from setuptools import setup, find_packages
from importlib.util import find_spec
import sys

sys.path.insert(0, ".")

import irhm

VERSION = irhm.__version__
DESCRIPTION = "IR-Drop Heatmap"
PROJECT = "irhm"
AUTHOR = irhm.__author__
EMAIL = irhm.__email__
URL = irhm.__url__

install_requires = [
    "numpy",
    "matplotlib",
    "seaborn ",
]

if find_spec("PySide6") is None:
    install_requires.append("PyQt5")
else:
    install_requires.append("PySide6")

setup(
    name=PROJECT,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    long_description=Path("README.md").read_text("utf-8"),
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    install_requires=install_requires,
    include_package_data=True,
    package_data={
        "irhm": ["icon.png"],
    },
    keywords=[
        PROJECT,
        "ic",
        "ir",
        "drop",
        "heatmap",
        "totem",
    ],
    entry_points={
        "console_scripts": [
            "irhm=irhm._main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Unix",
    ],
)
