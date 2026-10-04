import os
import random
import time

import requests
from dotenv import load_dotenv


# Load environment variables from the project's .env file.
load_dotenv()


# Deployed backend URL.
BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://cloud-based-vehicle-data-storage.onrender.com"
)

LOGIN_URL = f"{BASE_URL}/login"
TELEMETRY_URL = f"{BASE_URL}/telemetry"


# Authentication credentials.
USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "admin123"
)


# Vehicle database IDs.
VEHICLE_IDS = [1, 2, 3, 4]

# Telemetry upload interval.
SEND_INTERVAL = 5


def get_access_token():
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(
            LOGIN_URL,
            data=login_data,
            timeout=15
        )

        if response.status_code == 200:
            token_data = response.json()

            access_token = token_data.get(
                "access_token"
            )

            print("Authentication successful.")
            print("JWT token received.")

            return access_token

        print("Authentication failed.")
        print("Status:", response.status_code)
        print("Response:", response.text)

        return None

    except requests.exceptions.RequestException as error:
        print("Connection error while logging in:")
        print(error)

        return None


def generate_telemetry(vehicle_id):
    return {
        "vehicle_id": vehicle_id,

        "speed": round(
            random.uniform(30, 100),
            2
        ),

        "engine_rpm": round(
            random.uniform(1500, 3000),
            2
        ),

        "engine_temperature": round(
            random.uniform(75, 95),
            2
        ),

        "fuel_level": round(
            random.uniform(40, 90),
            2
        ),

        "battery_voltage": round(
            random.uniform(12.0, 14.2),
            2
        ),

        "latitude": round(
            12.2958 + random.uniform(
                -0.001,
                0.001
            ),
            6
        ),

        "longitude": round(
            76.6394 + random.uniform(
                -0.001,
                0.001
            ),
            6
        )
    }


def send_telemetry(
    vehicle_id,
    access_token
):
    telemetry = generate_telemetry(
        vehicle_id
    )

    headers = {
        "Authorization": (
            f"Bearer {access_token}"
        )
    }

    try:
        response = requests.post(
            TELEMETRY_URL,
            json=telemetry,
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            print(
                f"Vehicle {vehicle_id} "
                f"telemetry uploaded successfully."
            )

            print(
                f"  Speed: "
                f"{telemetry['speed']} km/h | "
                f"RPM: "
                f"{telemetry['engine_rpm']} | "
                f"Temperature: "
                f"{telemetry['engine_temperature']} °C | "
                f"Fuel: "
                f"{telemetry['fuel_level']}% | "
                f"Battery: "
                f"{telemetry['battery_voltage']} V"
            )

            return True

        elif response.status_code == 401:
            print(
                f"Vehicle {vehicle_id}: "
                "Authentication expired or invalid."
            )

            return False

        else:
            print(
                f"Vehicle {vehicle_id}: "
                "Telemetry upload failed."
            )

            print(
                "Status:",
                response.status_code
            )

            print(
                "Response:",
                response.text
            )

            return True

    except requests.exceptions.RequestException as error:
        print(
            f"Vehicle {vehicle_id}: "
            "Connection error."
        )

        print(error)

        return True


if __name__ == "__main__":

    print()
    print(
        "=========================================="
    )
    print(
        "   CLOUD VEHICLE TELEMETRY SIMULATOR"
    )
    print(
        "=========================================="
    )

    print(
        "Backend:",
        BASE_URL
    )

    print(
        "Vehicles:",
        ", ".join(
            f"VH{vehicle_id:03d}"
            for vehicle_id in VEHICLE_IDS
        )
    )

    print(
        "Telemetry interval:",
        SEND_INTERVAL,
        "seconds"
    )

    print()

    access_token = get_access_token()

    if not access_token:
        print()
        print(
            "Unable to authenticate."
        )

        print(
            "Make sure the Render backend "
            "is running and credentials are correct."
        )

        exit(1)

    print()
    print(
        "Starting cloud multi-vehicle telemetry..."
    )
    print()

    while True:

        for vehicle_id in VEHICLE_IDS:

            success = send_telemetry(
                vehicle_id,
                access_token
            )

            if not success:

                print()
                print(
                    "Authentication rejected."
                )

                print(
                    "Attempting to authenticate again..."
                )

                print()

                access_token = get_access_token()

                if not access_token:

                    print(
                        "Re-authentication failed."
                    )

                    time.sleep(5)

                    continue

                send_telemetry(
                    vehicle_id,
                    access_token
                )

        print()

        print(
            f"Waiting {SEND_INTERVAL} seconds..."
        )

        print()

        time.sleep(
            SEND_INTERVAL
        )