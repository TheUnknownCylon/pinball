import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pinball",
    version="0.0.1",
    author="TheUC",
    author_email="theunknowncylon@live.nl",
    description="Pinball controller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/theunknowncylon",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'tornado==4.3.0',
        'smbus2==0.2.1',
        'pyglet==1.2.4',
        'pyserial==2.7',
#        'pygame'
        ]
)

