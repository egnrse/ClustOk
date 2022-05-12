from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='clustOk',
    version='0.1.0',    
    description='A python tool to run and evaluate different kind of tests on clusters',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://hellogity.par.tuwien.ac.at/hinkel/clustok',
    author='Markus Hinkel',
    author_email='markus@markushinkel.com',
    packages=['clustOk'],
    install_requires=['fire', 'pyyaml', 'psutil', 'schema'],
    classifiers=[
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
