from setuptools import setup, find_packages

setup(
    name='good_feeder',
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm'
    ],
    install_requires=[
        'colorama',
        'feedreader',
        'requests',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'good_feeder = good_feeder.cli.main:main',
        ],
    },
)
