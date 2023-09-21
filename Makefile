n ?= 2

run: stop prune
	sh start.sh $(n)
stop: 
	-sh stop.sh
prune: 
	-docker container prune -f
	-docker volume prune -f
disconnect: 
	@echo "Disconnecting client connectors"
	@for i in {1..$(n)}; do \
		echo "Disconnecting client connector $$i"; \
		CONNECTOR_PORT=$$((8082+$$i)); \
		curl -i -X DELETE -H "Accept:application/json" http://localhost:$$CONNECTOR_PORT/connectors/client-$$i-connector; \
	done
	@echo 
	@echo "Disconnecting server connector"
	curl -i -X DELETE -H "Accept:application/json" http://localhost:7000/connectors/server-connector
connect: 
	@echo "Connecting client connectors"
	@for i in {1..$(n)}; do \
		echo "Connecting client connector $i"; \
		CONNECTOR_PORT=$$((8082+$$i)); \
		curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:$$CONNECTOR_PORT/connectors/ -d @db_client/register-postgres-$$i.json; \
	done
	@echo "Connecting server connector"
	curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" http://localhost:7000/connectors/ -d @server/register-postgres.json
