from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

DATA_FILE = "../logs/borewell_data.csv"


def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    # Remove invalid readings
    df = df[(df["Water_Level_cm"] >= 0) & (df["Water_Level_cm"] <= 120)]

    # Smooth noisy sensor data
    df["Water_Level_cm"] = df["Water_Level_cm"].rolling(5).mean()

    return df


@app.route("/")
def dashboard():

    df = load_data()

    if df.empty:
        return render_template("dashboard.html", data=None)

    latest = df.iloc[-1]

    data = {
        "time": latest["Time"],
        "water": round(latest["Water_Level_cm"], 2),
        "temp": latest["Temperature_C"],
        "humidity": latest["Humidity_%"],
        "pump": latest["Pump_Status"],
        "health": latest["Health_Status"]
    }

    return render_template("dashboard.html", data=data)


@app.route("/sensors")
def sensors():

    df = load_data()

    if df.empty:
        return render_template("sensors.html", data=[])

    rows = df.tail(20).to_dict(orient="records")

    return render_template("sensors.html", data=rows)


@app.route("/alerts")
def alerts():

    df = load_data()

    alerts = []

    if not df.empty:
        for _, row in df.tail(20).iterrows():
            if row["Health_Status"] != "HEALTHY":
                alerts.append(
                    f"{row['Time']} - {row['Health_Status']}"
                )

    return render_template("alerts.html", alerts=alerts)


@app.route("/trends")
def trends():

    df = load_data()

    if df.empty:
        return render_template("trends.html", times=[], water=[])

    times = df["Time"].tail(30).tolist()
    water = df["Water_Level_cm"].tail(30).tolist()

    return render_template(
        "trends.html",
        times=times,
        water=water
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
