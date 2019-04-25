# Prometheus

## Prometheus exporter for Pure Storage FlashArray and FlashBlade.

An exporter "gateway" for Pure Storage FlashArray and FlashBlade provided in a shape of Docker container.
The aim of this exporter is to provide an easy way to scrape a fleet of FlashArray and/or FlashBlade appliances by simply configuring a scrape config section with just a couple of parameters for each target appliance.

### Deployment

The exporter is a Python Flex application that is packaged as a Docker container and as such can be deployed straight on any docker engine linux host, which may also be the same machine hosting the Prometheus container (and possibly Grafana).

1. Verify the actual exposed tcp port in the Dockerfile is suited for your environment (defauls is 9091) and modify it if necessary.
2. Build the export image by running make in the project directory

       pureuser@build-host08:~/Monitoring/Prometheus$ sudo make

3. Run the final image

       pureuser@build-host08:~/Monitoring/Prometheus$ sudo run

### Metrics URLs

The exporter application uses a RESTful schema to provid Prometheus metrics. For a FlashArray appliance it must be invoked at the URL

    http://<exporter-ip>:<exporter-port>/metrics/flasharray

and for a FlashBlade appliance at the URL

    http://<exporter-ip>:<exporter-port>/metrics/flashblade

In both the cases it is necessary to specify two additional paramethers to identify and access the target appliance: the appliance hostname/IP address and the API token for a valid account on the same appliance. Therefore, the full URL schema to be used is as follows:

    FlashArray   http://<exporter-ip>:<exporter-port>/metrics/flasharray?endpoint=<fqdn_or_ip>&apitoken=<APItoken>
    FlashBlade   http://<exporter-ip>:<exporter-port>/metrics/flashblade?endpoint=<fqdn_or_ip>&apitoken=<APItoken>

### Prometheus configuration

To make full use of the statelessness of the exporter, we need to properly configure
prometheus relabeling.
The API key is given as a meta label, and will be placed into the request as a GET
parameter before the actual metrics scraping from the exporter happens.
Afterwards, the label will be dropped for security reasons.

Take this full prometheus configuration as a reference:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
# Job for all Pure Flasharrays
- job_name: 'pure_flasharray'
  metrics_path: /metrics/flasharray
  relabel_configs:
  # meta label of target address --> get parameter "pure_host"
  - source_labels: [__address__]
    target_label: __param_endpoint
  # label of target api token --> get parameter "pure_apitoken"
  - source_labels: [__pure__apitoken]
    target_label: __param_apitoken
  # display the pure host as the instance label
  - source_labels: [__address__]
    target_label: instance
  # point to the scraping endpoint of the exporter
  - target_label: __address__
    replacement: localhost:8080 # address of the exporter, in debug mode
                                # THIS NEEDS TO BE CHANGED TO YOUR ENVIRONMENT
  
  # Actual pure hosts (without a prometheus endpoint) as targets
  static_configs:
  - targets: [ mypureflasharray-01.lan ]
    labels:
      __pure__apitoken: 00000000-0000-0000-0000-000000000000

  - targets: [ mypureflasharray-02.lan ]
    labels:
      __pure__apitoken: 00000000-0000-0000-0000-000000000000


# Job for all Pure Flashblades
- job_name: 'pure_flashblade'
  metrics_path: /metrics/flashblade
  relabel_configs:
  # meta label of target address --> get parameter "pure_host"
  - source_labels: [__address__]
    target_label: __param_endpoint
  # label of target api token --> get parameter "pure_apitoken"
  - source_labels: [__pure__apitoken]
    target_label: __param_apitoken
  # display the pure host as the instance label
  - source_labels: [__address__]
    target_label: instance
  # point to the scraping endpoint of the exporter
  - target_label: __address__
    replacement: localhost:8080 # address of the exporter, in debug mode
                                # THIS NEEDS TO BE CHANGED TO YOUR ENVIRONMENT
    
  # Actual pure hosts (without a prometheus endpoint) as targets
  static_configs:
  - targets: [ mypureflashblade-01.lan ]
    labels:
      __pure__apitoken: 00000000-0000-0000-0000-000000000000

  - targets: [ mypureflashblade-02.lan ]
    labels:
      __pure__apitoken: 00000000-0000-0000-0000-000000000000
```

If you now check for the `up` prometheus metric, you would see the following:
```
up{job="pure_flasharray",instance="mypureflasharray-01.lan"} 1
up{job="pure_flasharray",instance="mypureflasharray-02.lan"} 1
up{job="pure_flashblade",instance="mypureflashblade-01.lan"} 1
up{job="pure_flashblade",instance="mypureflashblade-02.lan"} 1
```

The `job` label is static, the `instance` label represents the target system.
Of course, you can also add additional labels in the `labels:` section of the
static configs.

The actual scraping address (the one of the exporter application) is set via the
last relabel config. It never appears anywhere in the metrics, as it is fully
irrelevant.

## Authors

* **Eugenio Grosso**
* **Philipp Mollitor** - [PhilsLab](https://github.com/PhilsLab)

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
