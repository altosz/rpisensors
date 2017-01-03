from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name="rpisensors",
    version="0.1.0",
    description="Raspberry Pi Sensors",
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Topic :: System :: Hardware',
        'Topic :: Software Development :: Embedded Systems',
    ],
    url="https://github.com/altosz/rpisensors",
    author="Alexei Tishin",
    author_email="altos.z@gmail.com",
    license="GPLv2",
    packages=["rpisensors"],
    zip_safe=False
)
