from setuptools import setup, find_packages

version = '0.0.3'

LONG_DESCRIPTION = '''
testing
'''

setup(
	name='django-formsfive',
	version = version,
	description='django-formsfive',
	long_description=LONG_DESCRIPTION,
	classifiers=[
		""
	],
	keywords='forms,html5,django',
	author='Jay States',
	author_email='iam@jstat.es',
	url='http://github.com/iamjstates/django-formsfive',
	license='MIT',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
)