# syex
SYnology EXporter. Exports data from your synology machine to prometheus.

## Run it

```
# docker-compose.yml

services:
  synology-exporter:
    image: lilja/syex:latest
    container_name: syex
    ports:
      - 9999:9999
    environment:
      - SYNOLOGY_URL=192.168.0.100
      - SYNOLOGY_PORT=5000
      - SYNOLOGY_USER=USER_NAME
      - SYNOLOGY_PASSWORD=PASSWORD
      - SYNOLOGY_HTTPS="true"
      - SYNOLOGY_VERIFY_SSL="true"
      - FREQUENCY=1
```

`$ docker-compose up -d`


Prometheus config


```
  - job_name: synology-exporter
    static_configs:
      - targets: ['ip_address:9999']
```

