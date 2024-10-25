from setuptools import setup

install_requires=[
   'phidl','jupyter','jupyterlab','pandas'
]

setup(name='pirel',
      version='0.2',
      description='Python Package based on amccaugh\phidl for piezoelectric resonator GDS layout',
      author='Giuseppe Michetti',
      author_email='michetti.g@northeastern.edu',
      packages=['pirel','pirel.addOns'],
      install_requires=install_requires,
      py_modules=['pirel.tools','pirel.pcells','pirel.modifiers','pirel.sweeps']
     ),
