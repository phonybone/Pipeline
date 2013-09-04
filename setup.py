from distutils.core import setup

setup(name='Pipeline',
      description='a framework for creating and running command pipelines',
      version='0.002',
#      py_modules=['Pipeline', 'exceptions', 'host', 'run_cmd'],
      author='Victor Cassen',
      author_email='vcassen@systemsbiology.org',
      url='https://github.com/phonybone/Pipeline',
      packages=['Pipeline'],
      package_data={'Pipeline': ['config/logging.conf']},
)
