import setuptools

with open("README.md", "r") as fh:
      long_description = fh.read()

setuptools.setup(name='habsim',
      version='0.2',
      description='Client interface to Stanford Student Space Initiative HABSIM server',
      url='http://github.com/stanford-ssi/habsim_client',
      license='GNU GPLv3',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=setuptools.find_packages(),
      python_requires='>=3'
)
