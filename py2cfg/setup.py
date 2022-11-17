from setuptools import setup, find_packages

setup(
    name="py2cfg",
    packages=find_packages(),
    entry_points={"console_scripts": ["py2cfg=py2cfg._runner:main"]},
)
