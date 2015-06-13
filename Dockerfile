FROM python:3.4

MAINTAINER Byron Ruth <b@devel.io>

ADD . /src

# Install dependencies
RUN apt-get -qq update
RUN apt-get -qq install -y git postgresql

# Optional dependencies
RUN pip install -r /src/requirements.txt

# Install this package.
RUN pip -q install /src

EXPOSE 5000

ENTRYPOINT ["prov-extractor", "--host", "0.0.0.0"]
