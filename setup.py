from distutils.core import setup

setup(
    name='pytterrator',
    packages=['pytterrator'],
    version='0.0.1',
    license='MIT',
    description='A Python module to scrape twitter.',
    author='Ahmad Alkadri',
    author_email='ahmad.alkadri@outlook.com',
    install_requires=[
        'fake_useragent',
        'bs4',
        'requests',
        'urllib3',
        'numpy'
    ]
)
