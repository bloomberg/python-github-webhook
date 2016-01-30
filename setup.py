from setuptools import setup

setup(name="github-webhook",
      version="1.0",
      description="Very simple, but powerful, microframework for writing Github webhooks in Python",
      url="https://github.com/bloomberg/python-github-webhook",
      author="Alex Chamberlain, Fred Phillips, Daniel Kiss, Daniel Beer",
      author_email="achamberlai9@bloomberg.net, fphillips7@bloomberg.net, dkiss1@bloomberg.net, dbeer1@bloomberg.net",
      license='Apache 2.0',
      packages=["github_webhook"],
      install_requires=['flask'],
      test_suite='nose.collector')
