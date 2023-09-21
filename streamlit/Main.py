import streamlit as st

# Streamlit app
st.title("DAIMPL Praktikum")
st.subheader("Local First: Daten-Synchronisierung mit Postgres-CDC")
st.write("---")
st.markdown("""
Access the Todo List in the left Navigation bar and choose a client that this Window Represents.

Now you can interact with the todo list.

We do NOT have auto refreshing when new records arise in the Kafka Database for non-authoring clients.
So please use the refresh button in the left navigation bar after performing modifications if you open the application in multiple tabs for different clients.

If you only use one tab and switch between clients via the given select button it auto loads the current database content.

#### Examine the change events
A Redpanda GUI is running on [http://localhost:8080](http://localhost:8080)
Here you can gain insights into the current state of each topic.

#### Connecting and Disconnecting Clients
We implemented a simple Solution for simulating disconnection by disconnecting all Debezium Connectors  at once.

Using multiple Networks would suit the case better in order to simulate individual clients loosing their Internet connection but requires some knowledge about docker networking and Debezium Reconnection Settings for Kafka.

Disconnecting the connectors provides almost the same functionality.
We ensured that the behaviour is the same disconnecting connectors from the database as cutting the connection from each connector to kafka individually as well as interrupting the sync job by loosing connection.

To run the disconnect just type the following command. This disconnects the first *n* clients but always the Server.
We only tested this with using he same n as for the run command

	make disconnect n=<num_clients>

Changes that are made now are not beeing propagated.
As we create timestamps on clients, conflicts can now be created by performing dual writes, delete-write etc.

Please notice that on reconnecting, the client with the lowest id most probable will be the fastest to send its changes to kafka (First to reconnect due to for loop)

In case you want to see how the system handles update order you can experiment with changing Items on the higher numbered clients first and then on the lower numbered ones.

to reconnect the clients

	make connect n=<num_clients>

they will auto sync once the connectors are ready and continue reading from the server-topic at their last offset.
#### How to see what happens
We suggest opening a terminal for each client and one for the server. We provide detailed logs on each component.

To reduce the logging level on the server you can modify the servers [main.py](server/daimpl_sink/main.py) and change the logging level to INFO

to see the logs please use the following commands

Server Logs:

	docker logs daimpl-sink -f

Client Logs (Where *id = [1, 2, ..., n]*)

	docker logs client-<id>-backend -f

""")