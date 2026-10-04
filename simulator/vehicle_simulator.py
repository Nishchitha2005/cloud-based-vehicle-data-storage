import requests
import random
import time


# =========================================================
# CONFIGURATION
# =========================================================

BASE_URL = "http://127.0.0.1:8000"

LOGIN_URL = f"{BASE_URL}/login"
TELEMETRY_URL = f"{BASE_URL}/telemetry"

USERNAME = "admin"
PASSWORD = "admin123"

# Vehicle database IDs
VEHICLE_IDS = [1, 2, 3, 4]

# Time between telemetry transmissions
SEND_INTERVAL = 5


# =========================================================
# AUTHENTICATION
# =========================================================

def get_access_token():

    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:

        response = requests.post(
            LOGIN_URL,
            data=login_data
        )

        if response.status_code == 200:

            token_data = response.json()

            access_token = token_data.get(
                "access_token"
            )

            print("Authentication successful.")
            print("JWT token received.")

            return access_token

        else:

            print("Authentication failed.")
            print("Status:", response.status_code)
            print("Response:", response.text)

            return None

    except requests.exceptions.RequestException as error:

        print("Connection error while logging in:")
        print(error)

        return None


# =========================================================
# GENERATE TELEMETRY
# =========================================================

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


# =========================================================
# SEND TELEMETRY
# =========================================================

def send_telemetry(
    vehicle_id,
    access_token
):

    telemetry = generate_telemetry(
        vehicle_id
    )

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:

        response = requests.post(
            TELEMETRY_URL,
            json=telemetry,
            headers=headers
        )

        if response.status_code == 200:

            print(
                f"Vehicle {vehicle_id} "
                f"telemetry uploaded successfully."
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


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print("   MULTI-VEHICLE TELEMETRY SIMULATOR")
    print("======================================")

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

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    access_token = get_access_token()

    if not access_token:

        print()
        print("Unable to authenticate.")
        print(
            "Make sure the FastAPI server "
            "is running."
        )

        exit(1)

    print()
    print("Starting multi-vehicle telemetry...")
    print()

    # -----------------------------------------------------
    # CONTINUOUS TELEMETRY TRANSMISSION
    # -----------------------------------------------------

    while True:

        for vehicle_id in VEHICLE_IDS:

            success = send_telemetry(
                vehicle_id,
                access_token
            )

            # -------------------------------------------------
            # RE-AUTHENTICATE IF TOKEN IS INVALID
            # -------------------------------------------------

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

                # Retry current vehicle
                send_telemetry(
                    vehicle_id,
                    access_token
                )

        print()
        print(
            f"Waiting {SEND_INTERVAL} seconds..."
        )
        print()

        time.sleep(SEND_INTERVAL)