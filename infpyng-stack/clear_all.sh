docker-compose --project-name infpyng -f docker-compose.yml down
docker rmi $(docker images | grep grafana | awk '{print $3}')
docker rmi $(docker images | grep chronograf | awk '{print $3}')
docker rmi $(docker images| grep influxdb | awk '{print $3}')
docker rmi $(docker images | grep infpyng | awk '{print $3}')
rm -rf data/
