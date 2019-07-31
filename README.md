
## CO2 sensor readout and push to mqtt, in docker container on rpi - desinged for a K8S cluster

WIP

copied logic and code from:
* https://gitlab.com/nobodyinperson/co2monitor


kubernetes deployment config:
```
apiVersion: extensions/v1beta1
kind: Deployment
labels:
    app: co2-mqtt
    name: co2-mqtt
spec:
  replicas: 1
  selector:
    matchLabels:
      app: co2-mqtt
  template:
    metadata:
      labels:
        app: co2-mqtt
    spec:
      containers:
      - env:
        - name: USB_DEVICe
          value: /dev/hiddraw0
        - name:  MQTT_SERVER
          value: 192.168.1.1
        - name: MQTT_PORT
          value: 1883
        - name: MQTT_TOPIC
          value: co2/room_1

        image: sebastiand/co2-mqtt-pi:latest
        name: co2-mqtt
        tty: true
```