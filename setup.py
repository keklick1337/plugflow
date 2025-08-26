import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

# Import version from the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from plugflow._version import __version__

setuptools.setup(
    name='plugflow',
    version=__version__,
    author='Vladislav Tislenko',
    author_email='python@trustcrypt.com',
    description='A powerful Python plugin system with dynamic loading and hot-reload capabilities.',
    keywords='plugin, plugins, dynamic-loading, hot-reload, extensible, plugin-system, python-plugins',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/keklick1337/plugflow',
    project_urls={
        'Documentation': 'https://github.com/keklick1337/plugflow',
        'Bug Reports': 'https://github.com/keklick1337/plugflow/issues',
        'Source Code': 'https://github.com/keklick1337/plugflow',
        'Homepage': 'https://github.com/keklick1337/plugflow',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        'Development Status :: 4 - Beta',
        
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3 :: Only',
        

        
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[],
    extras_require={
        'dev': ['pytest', 'pytest-cov', 'black', 'isort'],
    },
    include_package_data=True,
    zip_safe=False,
)
