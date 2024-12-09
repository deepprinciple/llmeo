from setuptools import setup, find_packages


setup(
    name = 'dp-proj-llmeo',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    maintainer='Jieyu Lu, Zhangde Song, Chenru Duan',
    maintainer_email='duanchenru@gmail.com',
    packages=find_packages(exclude=('tests',)),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    license='MIT',
)