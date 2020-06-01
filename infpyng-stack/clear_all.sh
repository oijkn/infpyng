docker-compose --project-name infpyng -f docker-compose.yml down
docker rmi influxdb:latest
docker rmi chronograf:latest
docker rmi grafana/grafana:6.7.3
docker rmi oijkn/infpyng:latest
rm -rf data/
