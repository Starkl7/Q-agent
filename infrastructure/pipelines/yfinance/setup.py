from setuptools import setup, find_packages

setup(
    name='yfinance_lean',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'yfinance>=0.2.0',
        'pandas>=2.2.0',
    ],
)
