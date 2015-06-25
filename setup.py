from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

version = '0.0.4'

install_requires = [
    'python-etcd'
]

test_requires = [
    'nose',
    'robber'
]

setup(name='python-etcd-lock',
    version=version,
    description="A distributed lock recipe for etcd",
    long_description=README,
    classifiers=[
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Database :: Front-Ends",
    ],
    keywords='etcd distributed lock semaphore mutex',
    author='Nathan Black',
    author_email='nathan@appuri.com',
    url='https://github.com/appuri/python-etcd-lock',
    license='ISC',
    packages=['etcdlock'],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='nose.collector',

)