from setuptools import setup, find_packages

setup(
    name='addrs2lines',
    version='0.1',
    packages=find_packages(),
    entry_points={'console_scripts': ['addrs2lines=addrs2lines:main']},
)