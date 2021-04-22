![Current version](https://img.shields.io/github/v/tag/PureStorage-OpenConnect/pure-exporter?label=current%20version)

# Pure Storage Prometheus exporter
Prometheus exporter for Pure Storage FlashArrays and FlashBlades.


### Overview

This applications aims to help monitor Pure Storage FlashArrays and FlashBlades by providing an "exporter", which means it extracts data from the Purity API and converts it to a format which is easily readable by Prometheus.

The stateless design of the exporter allows for easy configuration management as well as scalability for a whole fleet of Pure Storage systems. Each time Prometheus scrapes metrics for a specific system, it should provide the hostname via GET parameter and the API token as Authorization token to this exporter.

---

**Note**: The previous method to provide the Pure API token via a GET parameter is now deprecated and will be removed in the next major version.

---

To monitor your Pure Storage appliances, you will need to create a new dedicated user on your array, and assign read-only permissions to it. Afterwards, you also have to create a new API key.
The exporter is provided as three different options:

- pure-exporter. Full exporter for both FlashArray and FlashBlade in a single bundle
- pure-fa-exporter.  FlashArray exporter
- pure-fb-exporter.  FlashBlade exporter


### Building and Deploying

The exporter is preferably built and launched via Docker. You can also scale the exporter deployment to multiple containers on Kubernetes thanks to the stateless nature of the application.

---

#### The official docker images are available at Quay.io

```shell
docker pull quay.io/purestorage/pure-exporter:1.2.5-a
```

or

```shell
docker pull quay.io/purestorage/pure-fa-exporter:1.2.5-a
```
or

```shell
docker pull quay.io/purestorage/pure-fb-exporter:1.2.5-a
```
---

To build and deploy the application via Docker, your local linux user should be added to the `docker` group in order to be able to communicate with the Docker daemon. (If this is not possible, you can still use <kbd>sudo</kbd>)

The detailed description on how to do that can be found on the [Docker](https://docs.docker.com/engine/install/) official documentation for your operating systemm 
To run a simple instance of the exporter, run:
```bash
make -f Makefile.fa test
make -f Makefile.fb test
make -f Makefile.mk test
```

The Makefile currently features these targets:
- **build** - builds the docker image with preconfigured tags.
- **test** - spins up a new docker container with all required parameters.


### Local development

The application is usually not run by itself, but rather with the gunicorn WSGI server. If you want to contribute to the development, you can run the exporter locally without a WSGI server, by executing the application directly.

The following commands are required for a development setup:
```bash
# it is recommended to use virtual python environments!
python -m venv env
source ./env/bin/activate

# install dependencies
python -m pip install -r requirements.txt

# run the application in debug mode
python pure_exporter.py
```
Use the same approach to modify the FlashArray and/or the FlashBlade exporter, by simply using the related requitements file.

### Scraping endpoints

The exporter uses a RESTful API schema to provide Prometheus scraping endpoints.

**Authentication**

Autentication is used by the exporter as the mechanism to cross authenticate to the scraped appliance, therefore for each array it is required to provide the REST API token for an account that has a 'readonly' role. The api-token must be provided in the http request using the HTTP Authorization header of type 'Bearer'. This is achieved by specifying the api-token value as the authorization parameter of the specific job in the Prometheus configuration file. As an alternative, it is possible to provide the api-token as a request argument, using the *apitoken* key. *Note* this option is deprecated and will be removed from the next releases.


The full exporter understands the following requests:

System | URL | GET parameters | description
---|---|---|---
FlashArray | http://\<exporter-host\>:\<port\>/metrics/flasharray | endpoint| Full array metrics
FlashArray | http://\<exporter-host\>:\<port\>/metrics/flasharray/array | endpoint | Array only metrics
FlashArray | http://\<exporter-host\>:\<port\>/metrics/flasharray/volumes | endpoint | Volumes only metrics
FlashArray | http://\<exporter-host\>:\<port\>/metrics/flasharray/hosts | endpoint | Hosts only metrics
FlashArray | http://\<exporter-host\>:\<port\>/metrics/flasharray/pods | endpoint| Pods only metrics
FlashBlade | http://\<exporter-host\>:\<port\>/metrics/flashblade | endpoint | Full array metrics
FlashBlade | http://\<exporter-host\>:\<port\>/metrics/flashblade/array | endpoint | Array only metrics
FlashBlade | http://\<exporter-host\>:\<port\>/metrics/flashblade/clients | endpoint | Clients only metrics
FlashBlade | http://\<exporter-host\>:\<port\>/metrics/flashblade/quotas | endpoint | Quotas only metrics


The FlashArray-only and FlashBlade only exporters use a slightly different schema, which consists of the removal of the flasharray|flashblade string from the path.

**FlashArray**

URL | GET parameters | description
---|---|---
http://\<exporter-host\>:\<port\>/metrics | endpoint | Full array metrics
http://\<exporter-host\>:\<port\>/metrics/array | endpoint | Array only metrics
http://\<exporter-host\>:\<port\>/metrics/volumes | endpoint | Volumes only metrics
http://\<exporter-host\>:\<port\>/metrics/hosts | endpoint | Hosts only metrics
http://\<exporter-host\>:\<port\>/metrics/pods | endpoint | Pods only metrics

**FlashBlade**

URL | GET parameters | description
---|---|---
http://\<exporter-host\>:\<port\>/metrics | endpoint | Full array metrics
http://\<exporter-host\>:\<port\>/metrics/array | endpoint | Array only metrics
http://\<exporter-host\>:\<port\>/metrics/clients | endpoint | Clients only metrics
http://\<exporter-host\>:\<port\>/metrics/quotas | endpoint | Quotas only metrics


Depending on the target array, scraping for the whole set of metrics could result into timeout issues, in which case it is suggested either to increase the scraping timeout or to scrape each single endpoint instead.


### Prometheus configuration examples

The [config](config) directory provides a couple of Prometheus configuration examples that can be used as the starting point to build your own solution.

### Usage example

In a typical production scenario, it is recommended to use a visual frontend for your metrics, such as [Grafana](https://github.com/grafana/grafana). Grafana allows you to use your Prometheus instance as a datasource, and create Graphs and other visualizations from PromQL queries. Grafana, Prometheus, are all easy to run as docker containers.

To spin up a very basic set of those containers, use the following commands:
```bash
# Pure exporter
docker run -d -p 9491:9491 --name pure-exporter quay.io/purestorage/pure-exporter:<version>

# Prometheus with config via bind-volume (create config first!)
docker run -d -p 9090:9090 --name=prometheus -v /tmp/prometheus-pure.yml:/etc/prometheus/prometheus.yml -v /tmp/prometheus-data:/prometheus prom/prometheus:latest

# Grafana
docker run -d -p 3000:3000 --name=grafana -v /tmp/grafana-data:/var/lib/grafana grafana/grafana
```
Please have a look at the documentation of each image/application for adequate configuration examples.


### Bugs and Limitations

* Pure FlashBlade REST APIs are not designed for efficiently reporting on full clients and objects quota KPIs, therefrore it is suggested to scrape the /metrics/flasblade/array preferrably and use the /metrics/flasblade/clients and /metrics/flasblade/quotas individually and with a lower frequency that the other. In any case, as a general rule, it is advisable to do not lower the scraping interval down to less than 30 sec. In case you experience timeout issues, you may want to increase the internal Gunicorn timeout by specifically setting the `--timeout` variable and appropriately reduce the scraping intervall as well.

* By default the number of workers spawn by Gunicorn is set to 2 and this is not optimal when monitoring a relatively large amount of arrays. The suggested approach is therefore to run the exporter with a number of workers that approximately matches the number of arrays to be scraped.


### License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
