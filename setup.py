from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="etlelk",
    packages=['etlelk'],
    version="0.0.6",
    author="Alex Lopes Pereira",
    author_email="alexlopespereira@gmail.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexlopespereira/etl_elk",
    download_url="https://github.com/alexlopespereira/etl_elk/archive/0.0.6.tar.gz",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    keywords=['elasticsearch', 'ETL'],
    install_requires=[
        'bleach==3.1.1',
        'certifi==2019.11.28',
        'cffi==1.14.0',
        'chardet==3.0.4',
        'cryptography==2.8',
        'docutils==0.16',
        'elasticsearch==7.5.1',
        'idna==2.9',
        'importlib-metadata==1.5.0',
        'jeepney==0.4.2',
        'keyring==21.1.0',
        'pkginfo==1.5.0.1',
        'pycparser==2.19',
        'Pygments==2.5.2',
        'readme-renderer==24.0',
        'requests==2.23.0',
        'requests-toolbelt==0.9.1',
        'SecretStorage==3.1.2',
        'six==1.14.0',
        'tqdm==4.43.0',
        'twine==3.1.1',
        'urllib3==1.25.8',
        'webencodings==0.5.1',
        'zipp==3.0.0'
      ],
    python_requires='>=3.6',
)