import json
import time
import requests
import paho.mqtt.client as mqtt

# -----------------------------
# MQTT SETTINGS
# -----------------------------
BROKER = "localhost"
PORT = 1883
TOPIC = "borewell/data"

# -----------------------------
# SMS GATEWAY SETTINGS
# -----------------------------
PHONE_GATEWAY_IP = "192.168.29.45"   # CHANGE THIS
PHONE_GATEWAY_PORT = "9090"

FARMER_PHONE = "91XXXXXXXXXX"        # CHANGE THIS

# -----------------------------
# ALERT CONTROL
# -----------------------------
ALERT_COOLDOWN = 1800   # 30 minutes

last_alert_time = 0


# -----------------------------
# SEND SMS FUNCTION
# -----------------------------
def send_sms(message):

    url = f"http://{PHONE_GATEWAY_IP}:{PHONE_GATEWAY_PORT}/sendsms"

    params = {
        "phone": FARMER_PHONE,
        "text": message
    }

    try:

        requests.get(url, params=params, timeout=5)

        print("SMS ALERT SENT")

    except Exception as e:

        print("SMS FAILED:", e)


# -----------------------------
# ANALYZE SENSOR DATA
# -----------------------------
def analyze(data):

    global last_alert_time

    water = data.get("water_level_cm")
    temp = data.get("temperature_c")
    pump = data.get("pump_status")

    print("DATA:", water, temp, pump)

    now = time.time()

    if now - last_alert_time < ALERT_COOLDOWN:
        return

    # DRY RUN RISK
    if water is not None and water < 15 and pump == "ON":

        message = "⚠ Borewell Alert: Possible Dry Run Risk. Water level very low."

        send_sms(message)

        last_alert_time = now

    # MOTOR OVERHEATING
    if temp is not None and temp > 45:

        message = "⚠ Borewell Alert: Motor temperature high."

        send_sms(message)

        last_alert_time = now


# -----------------------------
# MQTT CALLBACK
# -----------------------------
def on_connect(client, userdata, flags, rc):

    print("Connected to MQTT Broker")

    client.subscribe(TOPIC)


def on_message(client, userdata, msg):

    try:

        payload = json.loads(msg.payload.decode())

        print("MQTT MESSAGE:", payload)

        analyze(payload)

    except Exception as e:

        print("ERROR:", e)


# -----------------------------
# START SERVICE
# -----------------------------
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

print("Alert service started...")

client.loop_forever()

