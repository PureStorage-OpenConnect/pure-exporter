# Pure Storage Helper
Basic volumes and hosts information retriever for Pure Storage FlashArrays.


### Overview

This applications is meant to provide an ancillary method to correlate hosts to volumes and vice-versa from a Pure Storage FlashArray, in order to help visualizing the information for tools like Grafana.
In the usual utilization scenario, this application works in conjunction with the Pure Prometheus exporter, Prometheus and Grafana for monitoring Pure Storage FlashArray. 

### Building and Deploying

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

To run a simple instance of the helper, run:
```bash
make test
```

The Makefile currently features these targets:
- **build** - builds the docker image with preconfigured tags.
- **test** - spins up a new docker container with all required parameters.
- **all** - runs _build_ and then _test_


### Local development

The application is usually not run by itself, but rather with the gunicorn WSGI server. If you want to contribute to the development, you can run the helper locally without a WSGI server, by executing the application directly.

The following commands are required for a development setup:
```bash
# it is recommended to use virtual python environments!
python -m venv env
source ./env/bin/activate

# install dependencies
python -m pip install -r requirements.txt

# run the application in debug mode
python pure_helper.py
```


### Quering endpoints

The helper application uses a RESTful API schema to provide Prometheus scraping endpoints.

Type | URL | required GET parameters
---|---|---
host volumes | http://\<helper-host\>:\<port\>/flasharray/host/{host}/volume | endpoint, apitoken
volume hosts | http://\<helper-host\>:\<port\>/flasharray/volume/{volume}/host | endpoint, apitoken


    labels:
      __pure_apitoken: 00000000-0000-0000-0000-000000000000

  - targets: [ mypureflashblade-02.lan ]
    labels:
      __pure_apitoken: 00000000-0000-0000-0000-000000000000
```



### Usage example

In a typical production scenario, it is recommended to use this helper in combination with a visual frontend for your metrics, such as [Grafana](https://github.com/grafana/grafana). Grafana allows you to use your Prometheus instance as a datasource, and create Graphs and other visualizations from PromQL queries. Grafana and Prometheus, are all easy to run as docker containers.

To spin up the containers, use the following commands:
```bash
docker run -d -p 9000:9000 --name pure-helper purestorage/pure-helper:latest


### Authors

* **Eugenio Grosso**

### License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
