from setuptools import setup

with open('./requirements.txt', 'r') as requirements:
    requirements = requirements.read().split('\n')

setup(
    name="nostr",
    version="0.1.0",
    packages=["nostr"],
    install_requires=requirements
)