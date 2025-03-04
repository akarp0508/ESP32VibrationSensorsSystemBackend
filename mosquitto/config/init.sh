#!/bin/sh
set -e

PASSWD_FILE="/mosquitto/config/passwd"

# Stworzenie pliku z hasłem
touch "$PASSWD_FILE"

# Dodawanie hasła i nazwy użytkownika
if [ -n "$MQTT_USER" ] && [ -n "$MQTT_PASSWORD" ]; then
    echo "Setting MQTT user credentials..."
    mosquitto_passwd -b "$PASSWD_FILE" "$MQTT_USER" "$MQTT_PASSWORD"
fi

# Ustawienie odpowiednich uprawnień do pliku
chown mosquitto:mosquitto "$PASSWD_FILE"
chmod 600 "$PASSWD_FILE"

# Start Mosquitto
exec mosquitto -c /mosquitto/config/mosquitto.conf
