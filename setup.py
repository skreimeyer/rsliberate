from setuptools import setup

setup(
	name="rsliberate",
	packages=["rsliberate"],
	entry_points = {
		"console_scripts": [
			"liberate = rsliberate.__main__:main",
			"fixe0449 = rsliberate.e0449:run",
		]
	},
	)
