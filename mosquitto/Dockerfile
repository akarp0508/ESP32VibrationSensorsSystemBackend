FROM eclipse-mosquitto:latest

COPY config/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY config/init.sh /mosquitto/config/init.sh

RUN chmod +x /mosquitto/config/init.sh

EXPOSE 1883 9001

ENTRYPOINT ["/mosquitto/config/init.sh"]
