# /usr/bin/env python
# -*- coding: utf-8 -*-

"""

"""

from setuptools import setup, find_packages

setup(
    name='kser',
    version=open('VERSION', 'r').read().strip(),
    description="Kafka serialize python library",
    long_description=open('README.rst', 'r').read().strip(),
    classifiers=["Programming Language :: Python", ],
    keywords='',
    author='Cedric DUMAY',
    author_email='cedric.dumay@gmail.com',
    url='https://github.com/cdumay/kser',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    install_requires=open('requirements.txt', 'r').read().strip(),
    extras_require={
        'confluent': ['confluent-kafka'],
        'http': ['cdumay-rest-client>=0.1'],
        'crypto': ['csodium==0.0.3'],
        'pykafka': ['kafka-python'],
        'prometheus': ['prometheus_client'],
        'opentracing': ['cdumay-opentracing>=0.1.8']
    },
    entry_points="""
""",
)
