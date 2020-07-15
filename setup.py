from distutils.core import setup

setup(
    name="etlelk",
    packages=['etlelk'],
    version="0.0.31",
    license="GNU Lesser General Public License v3.0",
    description="A small example package",
    author="Alex Lopes Pereira",
    author_email="alexlopespereira@gmail.com",
    url="https://github.com/alexlopespereira/etl_elk",
    download_url="https://github.com/alexlopespereira/etl_elk/archive/0.0.31.tar.gz",
    keywords=['elasticsearch', 'ETL'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'bleach==3.1.1',
        'certifi==2019.9.11',
        'cffi==1.14.0',
        'chardet==3.0.4',
        'cryptography==2.8',
        'docutils==0.16',
        'elasticsearch==7.0.5',
        'idna==2.8',
        'importlib-metadata==1.5.0',
        'jeepney==0.4.2',
        'keyring==21.1.0',
        'pkginfo==1.5.0.1',
        'pycparser==2.19',
        'Pygments==2.5.2',
        'readme-renderer==24.0',
        'requests==2.22.0',
        'requests-toolbelt==0.9.1',
        'SecretStorage==3.1.2',
        'six==1.12.0',
        'tqdm==4.43.0',
        'twine==3.1.1',
        'urllib3==1.25.8',
        'webencodings==0.5.1',
        'zipp==3.0.0'
      ],
)

