from setuptools import setup, find_packages


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Plugins',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Internet :: WWW/HTTP',
    'Programming Language :: Python :: 3.7',
]

setup(
    name='migrate',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'trafaret>=1.2,<1.3',
        'requests>=2.20',
        'inflection>=0.3,<0.4',
        'attrs>=18.2',
        'python-freeipa',
        'click'
    ],
    extras_require={
        'test': [
            'flake8',
            'pytest',
            'responses',
        ]
    },
    description='FreeIPA backup and migration',
    long_description=open('README.rst').read(),
    url='https://github.com/datarobot',
    packages=find_packages(exclude=('tests',)),
    zip_safe=False,
    author='Yehor Nazarkin',
    author_email='yehor@datarobot.com',
    platforms=['OS Independent']
)
