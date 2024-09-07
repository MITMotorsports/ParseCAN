from setuptools import setup, find_packages

setup(
    name="MotoParseCAN",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "dataclasses",
        "intervaltree",
        "PyYAML",
        "pint",
        "numpy",
    ],
)
