from setuptools import setup, find_packages
import sys


setup(
    name='ip_trie',
    version='0.1',
    license='MIT',
    url='https://github.com/bbayles/ip_trie',

    description='Match IP addresses to networks',
    long_description=(
        'Builds on the ipaddress module to allow for matching of ip_address '
        'objects to ip_network objects.'
    ),

    author='Bo Bayles',
    author_email='bbayles@gmail.com',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='ipaddress ip_address ip_network trie',

    packages=find_packages(exclude=[]),
    test_suite='tests',
)
