mkdir -p data
mkdir -p data/grafana
mkdir -p data/grafana/plugins
chmod -R a+w data/grafana
touch data/infpyng.log
tar -zxf grafana-provisioning/dashboards/plugins/multibar-graph-panel_0.2.5.tar.gz -C data/grafana/plugins/
docker-compose --project-name infpyng -f docker-compose.yml up -d
