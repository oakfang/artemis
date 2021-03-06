from setuptools import setup

setup(
    name='artemis',
    version='0.1.4',
    packages=['artemis'],
    url='',
    license='',
    install_requires=["six", "tornado>=4.0", "schematics>=1.0", "tinydb>=2.1.0"],
    author='oakfang',
    description='Async Restful TinyDB Models'
)
