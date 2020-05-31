mkdir data
mkdir data/grafana
chmod a+w data/grafana
touch data/infpyng.log
docker-compose --project-name infpyng -f docker-compose.yml up -d
