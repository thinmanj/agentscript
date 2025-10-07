#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentscript",
    version="0.1.0",
    author="Julio Merino",
    author_email="julio@example.com",
    description="A declarative language for agentic program creation that transpiles to Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/julio/agentscript",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "isort",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentscript=agentscript.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)