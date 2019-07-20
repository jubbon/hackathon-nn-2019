OSM_DIR = ../../data/osm

all: osrm

osrm: osrm.human osrm.vehicle

osrm.human:
	mkdir -p $(OSM_DIR)/osrm/human
	cp $(OSM_DIR)/$(OSM_ORIGIN).osm.pbf $(OSM_DIR)/osrm/human/
	docker-compose run osrm.human osrm-extract -p /opt/foot.lua /data/$(OSM_ORIGIN).osm.pbf
	docker-compose run osrm.human osrm-partition /data/$(OSM_ORIGIN).osrm
	docker-compose run osrm.human osrm-customize /data/$(OSM_ORIGIN).osrm

osrm.vehicle:
	mkdir -p $(OSM_DIR)/osrm/vehicle
	cp $(OSM_DIR)/$(OSM_ORIGIN).osm.pbf $(OSM_DIR)/osrm/vehicle/
	docker-compose run osrm.vehicle osrm-extract -p /opt/car.lua /data/$(OSM_ORIGIN).osm.pbf
	docker-compose run osrm.vehicle osrm-partition /data/$(OSM_ORIGIN).osrm
	docker-compose run osrm.vehicle osrm-customize /data/$(OSM_ORIGIN).osrm

nominatim:
	mkdir -p $(OSM_DIR)/nominatim
	cp $(OSM_DIR)/$(OSM_ORIGIN).osm.pbf $(OSM_DIR)/nominatim/
	docker-compose run nominatim sh /app/init.sh /data/$(OSM_ORIGIN).osm.pbf postgresdata 4