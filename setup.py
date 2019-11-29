from setuptools import setup

setup(
    name='flag-access-control-system',
    author='None of your beeswax!',
    entry_points={
        'console_scripts': [
            'flag_access=flag_access.main:main'
        ]
    }
)
