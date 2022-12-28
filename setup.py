from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='nostr',
    version="0.0.1",
    packages=find_packages(include=['nostr']),
    python_requires='>3.6.0',
    url='https://github.com/jeffthibault/python-nostr',
    description="A Python library for making Nostr clients.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
    ],
)