from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)

from sqlalchemy.orm import Session

from jose import JWTError, jwt


from backend.app.database import (
    Base,
    engine,
    get_db
)

from backend.app.models.vehicle import (
    Vehicle
)

from backend.app.models.telemetry import (
    Telemetry
)

from backend.app.models.alert import (
    Alert
)

from backend.app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse
)

from backend.app.schemas.telemetry import (
    TelemetryCreate,
    TelemetryResponse
)

from backend.app.auth import (
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ADMIN_USERNAME,
    ADMIN_PASSWORD
)


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Cloud-Based Vehicle Data Storage",
    description=(
        "Vehicle telemetry storage, analytics, "
        "authentication and alert management API"
    ),
    version="1.0.0"
)


# =========================================================
# AUTHENTICATION
# =========================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get(
            "sub"
        )

        if username is None:

            raise credentials_exception

        return username

    except JWTError:

        raise credentials_exception


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {
        "message": (
            "Cloud-Based Vehicle Data Storage API "
            "is running"
        )
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    if (
        form_data.username != ADMIN_USERNAME
        or form_data.password != ADMIN_PASSWORD
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        data={
            "sub": form_data.username
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================================================
# REGISTER VEHICLE
# =========================================================

@app.post(
    "/vehicles",
    response_model=VehicleResponse
)
def create_vehicle(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    # Check vehicle ID
    existing_vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.vehicle_id
            == vehicle.vehicle_id
        )
        .first()
    )

    if existing_vehicle:

        raise HTTPException(
            status_code=400,
            detail="Vehicle ID already exists"
        )


    # Check VIN
    existing_vin = (
        db.query(Vehicle)
        .filter(
            Vehicle.vin == vehicle.vin
        )
        .first()
    )

    if existing_vin:

        raise HTTPException(
            status_code=400,
            detail="VIN already exists"
        )


    new_vehicle = Vehicle(
        vehicle_id=vehicle.vehicle_id,
        vin=vehicle.vin,
        manufacturer=vehicle.manufacturer,
        model=vehicle.model,
        year=vehicle.year
    )

    db.add(
        new_vehicle
    )

    db.commit()

    db.refresh(
        new_vehicle
    )

    return new_vehicle


# =========================================================
# GET ALL VEHICLES
# =========================================================

@app.get(
    "/vehicles",
    response_model=list[VehicleResponse]
)
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    vehicles = (
        db.query(Vehicle)
        .order_by(
            Vehicle.id
        )
        .all()
    )

    return vehicles


# =========================================================
# UPLOAD TELEMETRY
# =========================================================

@app.post(
    "/telemetry",
    response_model=TelemetryResponse
)
def create_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    # -----------------------------------------------------
    # VERIFY VEHICLE EXISTS
    # -----------------------------------------------------

    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id
            == telemetry.vehicle_id
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )


    # -----------------------------------------------------
    # STORE TELEMETRY
    # -----------------------------------------------------

    new_telemetry = Telemetry(
        vehicle_id=telemetry.vehicle_id,
        speed=telemetry.speed,
        engine_rpm=telemetry.engine_rpm,
        engine_temperature=(
            telemetry.engine_temperature
        ),
        fuel_level=telemetry.fuel_level,
        battery_voltage=(
            telemetry.battery_voltage
        ),
        latitude=telemetry.latitude,
        longitude=telemetry.longitude
    )

    db.add(
        new_telemetry
    )

    db.commit()

    db.refresh(
        new_telemetry
    )


    # -----------------------------------------------------
    # AUTOMATIC ALERT GENERATION
    # -----------------------------------------------------

    alerts_to_create = []


    # Overspeed
    if telemetry.speed > 100:

        alerts_to_create.append(
            Alert(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=new_telemetry.id,
                alert_type="OVERSPEED",
                severity="WARNING",
                message=(
                    f"Vehicle speed reached "
                    f"{telemetry.speed} km/h"
                )
            )
        )


    # Engine overheating
    if telemetry.engine_temperature > 95:

        alerts_to_create.append(
            Alert(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=new_telemetry.id,
                alert_type="ENGINE_OVERHEATING",
                severity="CRITICAL",
                message=(
                    "Engine temperature reached "
                    f"{telemetry.engine_temperature} °C"
                )
            )
        )


    # Low fuel
    if telemetry.fuel_level < 20:

        alerts_to_create.append(
            Alert(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=new_telemetry.id,
                alert_type="LOW_FUEL",
                severity="WARNING",
                message=(
                    f"Fuel level dropped to "
                    f"{telemetry.fuel_level}%"
                )
            )
        )


    # Low battery
    if telemetry.battery_voltage < 11.5:

        alerts_to_create.append(
            Alert(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=new_telemetry.id,
                alert_type="LOW_BATTERY",
                severity="CRITICAL",
                message=(
                    f"Battery voltage dropped to "
                    f"{telemetry.battery_voltage} V"
                )
            )
        )


    # Store generated alerts
    for alert in alerts_to_create:

        db.add(
            alert
        )

    db.commit()


    return new_telemetry


# =========================================================
# GET VEHICLE TELEMETRY
# =========================================================

@app.get(
    "/telemetry/{vehicle_id}",
    response_model=list[TelemetryResponse]
)
def get_telemetry(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    # Verify vehicle exists
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )


    telemetry_records = (
        db.query(Telemetry)
        .filter(
            Telemetry.vehicle_id
            == vehicle_id
        )
        .order_by(
            Telemetry.timestamp.asc()
        )
        .all()
    )

    return telemetry_records


# =========================================================
# ANALYTICS
# =========================================================

@app.get(
    "/analytics/{vehicle_id}"
)
def get_analytics(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    # Verify vehicle exists
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )


    telemetry_records = (
        db.query(Telemetry)
        .filter(
            Telemetry.vehicle_id
            == vehicle_id
        )
        .all()
    )


    # No records
    if not telemetry_records:

        return {
            "vehicle_id": vehicle_id,
            "total_records": 0,
            "average_speed": 0,
            "maximum_speed": 0,
            "average_rpm": 0,
            "maximum_temperature": 0,
            "minimum_fuel": 0,
            "average_battery_voltage": 0
        }


    # Extract values
    speeds = [
        record.speed
        for record in telemetry_records
    ]

    rpms = [
        record.engine_rpm
        for record in telemetry_records
    ]

    temperatures = [
        record.engine_temperature
        for record in telemetry_records
    ]

    fuel_levels = [
        record.fuel_level
        for record in telemetry_records
    ]

    battery_voltages = [
        record.battery_voltage
        for record in telemetry_records
    ]


    return {
        "vehicle_id": vehicle_id,

        "total_records": len(
            telemetry_records
        ),

        "average_speed": round(
            sum(speeds) / len(speeds),
            2
        ),

        "maximum_speed": round(
            max(speeds),
            2
        ),

        "average_rpm": round(
            sum(rpms) / len(rpms),
            2
        ),

        "maximum_temperature": round(
            max(temperatures),
            2
        ),

        "minimum_fuel": round(
            min(fuel_levels),
            2
        ),

        "average_battery_voltage": round(
            sum(battery_voltages)
            / len(battery_voltages),
            2
        )
    }


# =========================================================
# GET VEHICLE ALERTS
# =========================================================

@app.get(
    "/alerts/{vehicle_id}"
)
def get_alerts(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):

    # Verify vehicle exists
    vehicle = (
        db.query(Vehicle)
        .filter(
            Vehicle.id == vehicle_id
        )
        .first()
    )

    if not vehicle:

        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )


    alerts = (
        db.query(Alert)
        .filter(
            Alert.vehicle_id
            == vehicle_id
        )
        .order_by(
            Alert.timestamp.desc()
        )
        .all()
    )

    return alerts