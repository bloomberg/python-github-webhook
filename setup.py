from setuptools import setup

setup(
    name="github-webhook",
    version="1.0.2",
    description="Very simple, but powerful, microframework for writing Github webhooks in Python",
    url="https://github.com/bloomberg/python-github-webhook",
    author="Alex Chamberlain, Fred Phillips, Daniel Kiss, Daniel Beer",
    author_email="achamberlai9@bloomberg.net, fphillips7@bloomberg.net, dkiss1@bloomberg.net, dbeer1@bloomberg.net",
    license="Apache 2.0",
    packages=["github_webhook"],
    install_requires=["flask", "six"],
    tests_require=["mock", "pytest"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Version Control",
    ],
    test_suite="nose.collector",
)
