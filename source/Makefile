TARGET_DIR = ../data/$(REGION_UID)

all: boundary h3 h3_to_geojson calc_population create-environment check-environment

boundary:
	@mkdir -p $(TARGET_DIR)/region/
	@inv boundary --region-name='$(REGION_NAME)' > $(TARGET_DIR)/region/boundary.json

h3:
	cat $(TARGET_DIR)/region/boundary.json | inv split-region --resolution=7 > $(TARGET_DIR)/region/indexes.7.h3
	cat $(TARGET_DIR)/region/boundary.json | inv split-region --resolution=8 > $(TARGET_DIR)/region/indexes.8.h3
	cat $(TARGET_DIR)/region/boundary.json | inv split-region --resolution=9 > $(TARGET_DIR)/region/indexes.9.h3
	cat $(TARGET_DIR)/region/boundary.json | inv split-region --resolution=10 > $(TARGET_DIR)/region/indexes.10.h3

h3_to_geojson:
	cat $(TARGET_DIR)/region/indexes.7.h3 | inv indexes-to-geojson > $(TARGET_DIR)/region/indexes.7.geojson
	cat $(TARGET_DIR)/region/indexes.8.h3 | inv indexes-to-geojson > $(TARGET_DIR)/region/indexes.8.geojson
	cat $(TARGET_DIR)/region/indexes.9.h3 | inv indexes-to-geojson > $(TARGET_DIR)/region/indexes.9.geojson
	cat $(TARGET_DIR)/region/indexes.10.h3 | inv indexes-to-geojson > $(TARGET_DIR)/region/indexes.10.geojson

trace_route:
	# Трассировка маршрутов общественного транспорта
	# Вычисление времени, которое занимает поездка от одной остановки до другой
	inv trace-route --route-dir=${TARGET_DIR}/routes --osrm-url='http://localhost:5001' --stop-time=45

geocode:
	# Геокодирование адресов жилых домов
	GEOCODER_PROVIDER=osm NOMINATIM_URL='http://localhost:9090/search' docker-compose up --build geocoder

calc_population:
	# Вычисление примерного количества людей, постоянно проживающего в каждой геообласти
	inv calc-population --path='$(TARGET_DIR)/houses' --total-population=${REGION_POPULATION} --resolution=7 > $(TARGET_DIR)/houses/population.7.geojson
	inv calc-population --path='$(TARGET_DIR)/houses' --total-population=${REGION_POPULATION} --resolution=8 > $(TARGET_DIR)/houses/population.8.geojson
	inv calc-population --path='$(TARGET_DIR)/houses' --total-population=${REGION_POPULATION} --resolution=9 > $(TARGET_DIR)/houses/population.9.geojson
	inv calc-population --path='$(TARGET_DIR)/houses' --total-population=${REGION_POPULATION} --resolution=10 > $(TARGET_DIR)/houses/population.10.geojson

fetch_infrastructure_objects:
	@mkdir -p $(TARGET_DIR)/infrastructure/
	# Здоровье
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Больница" > "$(TARGET_DIR)/infrastructure/Больница.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Поликлиника" > "$(TARGET_DIR)/infrastructure/Поликлиника.geojson"

	# Учеба
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="ВУЗ" > "$(TARGET_DIR)/infrastructure/ВУЗ.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Колледж" > "$(TARGET_DIR)/infrastructure/Колледж.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Училище" > "$(TARGET_DIR)/infrastructure/Училище.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Техникум" > "$(TARGET_DIR)/infrastructure/Техникум.geojson"

	# Торговля
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Торговый Центр" > "$(TARGET_DIR)/infrastructure/Торговый Центр.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Рынок" > "$(TARGET_DIR)/infrastructure/Рынок.geojson"

	# Спортивные объекты
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Стадион" > "$(TARGET_DIR)/infrastructure/Стадион.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Фитнес" > "$(TARGET_DIR)/infrastructure/Фитнес.geojson"

	# Парки
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Парки" > "$(TARGET_DIR)/infrastructure/Парки.geojson"

	# Заводы и т.п.
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Завод" > "$(TARGET_DIR)/infrastructure/Завод.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Фабрика" > "$(TARGET_DIR)/infrastructure/Фабрика.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Предприятие" > "$(TARGET_DIR)/infrastructure/Предприятие.geojson"

	# Объекты транспортной инфраструктуры
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Вокзал" > "$(TARGET_DIR)/infrastructure/Вокзал.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Станция" > "$(TARGET_DIR)/infrastructure/Станция.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Аэропорт" > "$(TARGET_DIR)/infrastructure/Аэропорт.geojson"

	# Развлечение
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Кинотеатр" > "$(TARGET_DIR)/infrastructure/Кинотеатр.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Театр" > "$(TARGET_DIR)/infrastructure/Театр.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Ночной клуб" > "$(TARGET_DIR)/infrastructure/Ночной клуб.geojson"

	# Достопримечательности
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Кремль" > "$(TARGET_DIR)/infrastructure/Кремль.geojson"

	# Храмы, соборы, мечети
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Храм" > "$(TARGET_DIR)/infrastructure/Храм.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Собор" > "$(TARGET_DIR)/infrastructure/Собор.geojson"
	inv fetch-poi --apikey=${YANDEX_API_KEY} --bbox=${YANDEX_MAP_BBOX} --query="Мечеть" > "$(TARGET_DIR)/infrastructure/Мечеть.geojson"

create-environment:
	@mkdir -p $(TARGET_DIR)/environments
	inv create-environment --path='$(TARGET_DIR)' --resolution=7 --output-format=json > "$(TARGET_DIR)/environments/environment.7.json"
	inv create-environment --path='$(TARGET_DIR)' --resolution=8 --output-format=json > "$(TARGET_DIR)/environments/environment.8.json"
	inv create-environment --path='$(TARGET_DIR)' --resolution=9 --output-format=json > "$(TARGET_DIR)/environments/environment.9.json"
	inv create-environment --path='$(TARGET_DIR)' --resolution=10 --output-format=json > "$(TARGET_DIR)/environments/environment.10.json"

	inv create-environment --path='$(TARGET_DIR)' --resolution=7 --output-format=geojson > "$(TARGET_DIR)/environments/environment.7.geojson"
	inv create-environment --path='$(TARGET_DIR)' --resolution=8 --output-format=geojson > "$(TARGET_DIR)/environments/environment.8.geojson"
	inv create-environment --path='$(TARGET_DIR)' --resolution=9 --output-format=geojson > "$(TARGET_DIR)/environments/environment.9.geojson"
	inv create-environment --path='$(TARGET_DIR)' --resolution=10 --output-format=geojson > "$(TARGET_DIR)/environments/environment.10.geojson"

check-environment:
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.7.json"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.8.json"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.9.json"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.10.json"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.7.geojson"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.8.geojson"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.9.geojson"
	inv check-environment --filename="$(TARGET_DIR)/environments/environment.10.geojson"

simulate:
	H3_RES=8 docker-compose up --build simulator

make-migration:
	inv make-migration --filename="$(TARGET_DIR)/playbooks/example.csv" > "$(TARGET_DIR)/playbooks/example-1.csv"