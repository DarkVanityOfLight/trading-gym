from setuptools import setup, find_packages

setup(
    name='trading-gym',
    version='0.1.0',
    description='Provides utils to train a trading AI',
    author='DarkVanityOfLight',
    author_email='darkvanity.oflight@gmail.com',
    license='BSD 2-clause',
    packages=find_packages(),
    install_requires=['matplotlib', 'tensorflow', 'tf-agents'],
)
