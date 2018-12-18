from setuptools import setup, find_packages

setup(
    name='sms_sender',
    version='0.1.2',
    packages=find_packages(exclude=['*.pyc']),
    include_package_data=True,
    zip_safe=False,
    url='',
    license='Proprietary',
    author='Daniyar Chambylov',
    author_email='dan.chambylov@gmail.com',
    description='sms sender',
    install_requires=[
        'django',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ],
)
