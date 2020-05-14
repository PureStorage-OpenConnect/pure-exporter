# Stack template for a monitoring system tool.

Components:
- Prometheus
- Grafana
- AlertManager
- Pure Storage metrics exporter for Prometheus
- Pure Storage FlashArray helper for Grafana 

You are required to provide the persistent storage for Prometheus and Grafana and modify the docker-compose.yaml file appropriately

### Usage example

To compose and launch the stack, use the following command:
```bash
sudo docker-compose -p <prefix_application> up -d
### License

This project is licensed under the Apache 2.0 License - see the [LICENSE.md](LICENSE.md) file for details
