#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0.txt
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from setuptools import setup

with open("README.rst", "r") as fp:
    long_description = fp.read()

with open("requirements.txt", "r") as fp:
    requirements = list(filter(bool, (line.strip() for line in fp)))

setup(
    name="rap_sitkcore",
    author="Bradley Lowekamp",
    author_email="bioinformatics@niaid.nih.gov",
    description="A template for python packages with best practices.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=["rap_sitkcore"],
    package_data={"rap_sitkcore": ["data/*"]},
    url="https://www.niaid.nih.gov/research/bioinformatics-computational-biosciences-branch",
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)
