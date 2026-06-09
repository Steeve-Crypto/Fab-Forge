import paho.mqtt.client as mqtt
import time
import json
import threading

class FabMQTTClient:
    def __init__(self, broker="localhost", port=1883):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.broker = broker
        self.port = port
        self.connected = False
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with code {rc}")
        self.connected = True
        self.client.subscribe("fab/#")
    
    def on_message(self, client, userdata, msg):
        print(f"Received on {msg.topic}: {msg.payload.decode()}")
        # Simulate control action
        if "command" in msg.payload.decode():
            print("Executing equipment command...")
    
    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            threading.Thread(target=self.client.loop_forever, daemon=True).start()
            time.sleep(1)
            return True
        except Exception as e:
            print(f"MQTT connection error: {e}")
            return False
    
    def publish(self, topic, message):
        payload = json.dumps(message) if isinstance(message, dict) else str(message)
        self.client.publish(topic, payload)
        print(f"Published to {topic}: {payload}")

# Example usage
if __name__ == "__main__":
    client = FabMQTTClient()
    if client.connect():
        client.publish("fab/sensor/temp", {"value": 250.5, "unit": "C"})
        time.sleep(2)
