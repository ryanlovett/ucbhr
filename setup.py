import setuptools

setuptools.setup(
	name='ucbhr',
	version='0.1',
	description='Query the UC Berkeley HRMS.',
	url='https://github.com/ryanlovett/ucbhr',
	author='Ryan Lovett',
	author_email='rylo@berkeley.edu',
	packages=setuptools.find_packages(),
	install_requires=[
	  'requests'
	],
    entry_points={
        'console_scripts': [
            'ucbhr= ucbhr.__main__:run',
        ],
    },

)
