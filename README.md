# Prometheus

## Prometheus exporter for Pure Storage FlashArray and FlashBlade.

An exporter "gateway" for Pure Storage FlashArray and FlashBlade provided in a shape of Docker container.
The aim of this exporter is to provide an easy way to scrape a fleet of FlashArray and/or FlashBlade appliances by simply configuring a scrape config section with just a couple of parameters for each target appliance.

### Deployment

The exporter is a Python Flex application that is packaged as a Docker container and as such can be deployed straight on any docker engine linux host, which may also be the same machine hosting the Prometheus container (and possibly Grafana).

1. Verify the actual exposed tcp port in the Dockerfile is suited for your environment (defauls is 9091) and modify it if necessary.
2. Build the export image by running make in the project directory

       pureuser@build-host08:~/python-virtual-environments/work/Monitoring/Prometheus$ sudo make

3. Run the final image

       pureuser@build-host08:~/python-virtual-environments/work/Monitoring/Prometheus$ sudo run

### Metrics URLs

The exporter application uses a RESTful schema to provid Prometheus metrics. For a FlashArray appliance it must be invoked at the URL

    http://<exporter-ip>:<exporter-port>/metrics/flasharray

and for a FlashBlade appliance at the URL

    http://<exporter-ip>:<exporter-port>/metrics/flashblade

In both the cases it is necessary to specify two additional paramethers to identify and access the target appliance: the appliance hostname/IP address and the API token for a valid account on the same appliance. Therefore, the full URL schema to be used is as follows:

    FlashArray     http://<exporter-ip>:<exporter-port>/metrics/flasharray?endpoint=<fqdn_or_ip>&api-token=<APItoken>
    FlashBlade     http://<exporter-ip>:<exporter-port>/metrics/flashblade?endpoint=<fqdn_or_ip>&api-token=<APItoken>

### Prometheus configuration

A possible configuration of the prometheus.yaml scrape section looks like the following

    global:
    
    ...
    
    scrape_configs:
    - job_name: x20-prod01
      metrics_path: /metrics/flasharray
      static_configs:
      - targets:
        - 192.168.103.110:9491
      params:
        endpoint: ['172.16.10.80']
        api-token: ['5d8ad02f-547d-fc24-bb51-fa0d2b0de973']
    - job_name: fb01
      metrics_path: /metrics/flashblade
      static_configs:
      - targets:
        - 192.168.103.110:9491
      params:
        endpoint: ['172.16.10.113']
        api-token: ['T-77ed85aa-d7b1-45cf-ab14-7b5c26ecea01']
