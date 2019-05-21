# Pure Storage Prometheus exporter
Prometheus exporter for Pure Storage FlashArrays and FlashBlades.


### Overview

This applications aims to help monitor Pure Storage FlashArrays and FlashBlades by providing an "exporter", which means it extracts data from the Purity API and converts it to a format which is easily readable by Prometheus.

The stateless design of the exporter allows for easy configuration management as well as scalability for a whole fleet of Pure Storage systems. Each time Prometheus scrapes metrics for a specific system, it should provide the hostname and the readonly API token via GET parameters to this exporter.

To monitor your Pure Storage hosts, you will need to create a new dedicated user on your array, and assign read-only permissions to it. Afterwards, you also have to create a new API key.


### Building and Deploying

The exporter is preferably built and launched via Docker. You can also scale the exporter deployment to multiple containers on Kubernetes thanks to the stateless nature of the application.

To build and deploy the application via Docker, your local linux user should be added to the `docker` group in order to be able to communicate with the Docker daemon. (If this is not possible, you can still use <kbd>sudo</kbd>)

This can be done with this command in the context of your user:
```bash
# add user to group
sudo usermod -aG docker $(whoami)
# apply the new group (no logout required)
newgrp docker
```

An included Makefile takes care of the necessary build steps:
```bash
make
```

To run a simple instance of the exporter, run:
```bash
make test
```

The Makefile currently features these targets:
- **build** - builds the docker image with preconfigured tags.
- **test** - spins up a new docker container with all required parameters.
- **all** - runs _build_ and then _test_


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


### Metrics URLs

The exporter application uses a RESTful API schema to provide Prometheus scraping endpoints.

Pure Storage System | URL | required GET parameters
---|---|---
FlashArray | http://\<exporter-host\>:\<port\>/metrics/flasharray | endpoint, apitoken
FlashBlade | http://\<exporter-host\>:\<port\>/metrics/flashblade | endpoint, apitoken


### Prometheus configuration

To make full use of the statelessness of the exporter, it is required to use some tricky relabeling rules.
The API key is given as a *meta label*, and will then be placed into the request as a GET parameter before the actual metrics scraping from the exporter happens. Afterwards, the label will be dropped for security reasons so it does not appear in the actual Prometheus database.

Take this full Prometheus configuration as a reference:
```yaml
global:
  # How often should Prometheus fetch metrics?
  # Recommended: 10s, 30s, 1m or 5m
  scrape_interval: 10s

scrape_configs:
# Job for all Pure Flasharrays
- job_name: 'pure_flasharray'
  metrics_path: /metrics/flasharray
  relabel_configs:
  # meta label of target address --> get parameter "pure_host"
  - source_labels: [__address__]
    target_label: __param_endpoint
  # label of target api token --> get parameter "pure_apitoken"
  - source_labels: [__pure_apitoken]
    target_label: __param_apitoken
  # display the pure host as the instance label
  - source_labels: [__address__]
    target_label: instance
  # point the exporter to the scraping endpoint of the exporter
  - target_label: __address__
    replacement: localhost:9491 # address of the exporter, in debug mode
                                # THIS NEEDS TO BE CHANGED TO YOUR ENVIRONMENT
  
  # Actual pure hosts (without a prometheus endpoint) as targets
  static_configs:
  - targets: [ mypureflasharray-01.lan ]
    labels: [ __pure_apitoken: 00000000-0000-0000-0000-000000000000 ]

  - targets: [ mypureflasharray-02.lan ]
    labels: [ __pure_apitoken: 00000000-0000-0000-0000-000000000000 ]


# Job for all Pure Flashblades
- job_name: 'pure_flashblade'
  metrics_path: /metrics/flashblade
  relabel_configs:
  # meta label of target address --> get parameter "pure_host"
  - source_labels: [__address__]
    target_label: __param_endpoint
  # label of target api token --> get parameter "pure_apitoken"
  - source_labels: [__pure_apitoken]
    target_label: __param_apitoken
  # display the pure host as the instance label
  - source_labels: [__address__]
    target_label: instance
  # point the exporter to the scraping endpoint of the exporter
  - target_label: __address__
    replacement: localhost:9491 # address of the exporter, in debug mode
                                # THIS NEEDS TO BE CHANGED TO YOUR ENVIRONMENT
    
  # Actual pure hosts (without a prometheus endpoint) as targets
  static_configs:
  - targets: [ mypureflashblade-01.lan ]
    labels: [ __pure_apitoken: 00000000-0000-0000-0000-000000000000 ]

  - targets: [ mypureflashblade-02.lan ]
    labels: [ __pure_apitoken: 00000000-0000-0000-0000-000000000000 ]
```

If you now check for the <kbd>up</kbd> metric in Prometheus, the result could look something like this:
```
up{job="pure_flasharray",instance="mypureflasharray-01.lan"} 1
up{job="pure_flasharray",instance="mypureflasharray-02.lan"} 1
up{job="pure_flashblade",instance="mypureflashblade-01.lan"} 1
up{job="pure_flashblade",instance="mypureflashblade-02.lan"} 1
```

The <kbd>job</kbd> label is statically configured via Prometheus, and is only used to identify the type of the metrics source. All hosts of the same type should share the same job label. The <kbd>instance</kbd> should be unique for each individual target, usually it is the FQDN.

If you want to provide additional static labels for each host you can add those at each targets "label" section in the Prometheus configuration file.
Good examples for additional labels are:
- location: us
- datacenter: mountain-view-1
- is_production: 1


### Usage example

In a typical production scenario, it is recommended to use a visual frontend for your metrics, such as [Grafana](https://github.com/grafana/grafana). Grafana allows you to use your Prometheus instance as a datasource, and create Graphs and other visualizations from PromQL queries. Grafana, Prometheus, are all easy to run as docker containers.

To spin up a very basic set of those containers, use the following commands:
```
# Pure exporter
docker run -d -p 9491:9491 --name pure-exporter purestorage/pure-exporter:latest

# Prometheus with config via bind-volume
docker run -d -p 9090:9090 --name=prometheus -v /tmp/prometheus-pure.yml:/etc/prometheus/prometheus.yml -v /tmp/prometheus-data:/prometheus prom/prometheus:latest

# Grafana
docker run -d -p 3000:3000 --name=grafana -v /tmp/grafana-data:/var/lib/grafana grafana/grafana
```
Please have a look at each the documentation of each image/application for adequate configuration examples.

A more robust example using docker-compose including Grafana, Prometheus and an exporter (in this case, netdata for linux) can be found [here](https://github.com/PhilsLab/gpn-docker).


### Authors

* **Eugenio Grosso**
* **Philipp Molitor** - [PhilsLab](https://github.com/PhilsLab)


### License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
