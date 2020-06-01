mkdir -p data
mkdir -p data/grafana
chmod -R a+w data/grafana
touch data/infpyng.log
docker-compose --project-name infpyng -f docker-compose.yml up -d
