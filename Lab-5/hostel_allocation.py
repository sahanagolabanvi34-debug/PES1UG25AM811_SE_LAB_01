"""Manage hostel room allocation and student records."""
import os
import secrets
import yaml
from flask import Flask, request
from markupsafe import escape

# Global hostel state
rooms = {}
allocations = {}
waitlist = []
app = Flask(__name__)


CONFIG = """
blocks:
  A: {gender: M, rooms: 3, capacity: 2, fee: 4000}
  B: {gender: F, rooms: 2, capacity: 3, fee: 3500}
"""


def load_config(text=CONFIG):
    """Load hostel configuration and initialize rooms."""
    config = yaml.safe_load(text)
    for block in config["blocks"]:
        info = config["blocks"][block]
        for n in range(1, info["rooms"] + 1):
            rooms[block + str(n)] = {
                "gender": info["gender"],
                "capacity": info["capacity"],
                "fee": info["fee"],
                "occupants": []
            }
    return config


def allocate_room(student_id, name, gender, year, preferred=None):
    """Allocate an available hostel room to a student."""
    if preferred is None:
        preferred = []
    if not isinstance(year, int):
        return None
    if student_id in allocations:
        return None
    for room_no in preferred + list(rooms.keys()):
        room = rooms[room_no]
        if room["gender"] != gender:
            continue
        if len(room["occupants"]) >= room["capacity"]:
            continue
        room["occupants"].append(student_id)
        allocations[student_id] = {"name": name, "room": room_no, "year": year}
        return room_no
    waitlist.append(student_id)


def vacate_room(student_id):
    """Remove a student from their allocated hostel room."""
    if student_id in allocations:
        room_no = allocations[student_id]["room"]
        rooms[room_no]["occupants"].remove(student_id)
        del allocations[student_id]


def monthly_fee(student_id, days_stayed):
    """Calculate hostel fees based on the number of days stayed."""
    room = rooms[allocations[student_id]["room"]]
    months = (days_stayed + 29) // 30
    return months * room["fee"]


def priority_order(students):
    """Sort students by year, giving senior students first priority."""
    return sorted(students, key=lambda s: s["year"], reverse=True)


def room_lottery(student_ids):
    """Randomly shuffle student IDs using secure randomness."""
    shuffled = list(student_ids)
    secure_random = secrets.SystemRandom()
    secure_random.shuffle(shuffled)
    return shuffled


def vacant_beds():
    """Calculate the total number of available hostel beds."""
    total = 0
    for room in rooms.values():
        total += room["capacity"] - len(room["occupants"])
    return total


def connect_warden_db():
    """Create a simulated warden database connection."""
    return sqlite_connect(
        host="localhost",
        user="warden",
        password=os.environ.get("HOSTEL_DB_PASSWORD", "")
    )


def sqlite_connect(host, user, password):
    """Simulate a database connection using the provided credentials."""
    return {"host": host, "user": user, "connected": len(password) > 0}


@app.route("/room")
def room_lookup():
    """Display the room allocation details for a student."""
    sid = request.args.get("id", "")
    allocation = allocations.get(sid)
    return f"<h1>Room for {escape(sid)}: {escape(str(allocation))}</h1>"


def run_portal():
    """Start the Flask hostel portal with debug mode disabled."""
    app.run(debug=False)


def main():
    """Run the hostel allocation system and display sample results."""
    load_config()
    print("Rooms:", list(rooms.keys()))
    print("S1 ->", allocate_room("S1", "Arjun", "M", 1))
    print("S2 ->", allocate_room("S2", "Kabir", "M", 2))
    print("S3 ->", allocate_room("S3", "Rohan", "M", 3))
    print("S4 (female) ->", allocate_room("S4", "Diya", "F", 1))
    print("S1 again ->", allocate_room("S1", "Arjun", "M", 1))
    print("S5 year '2' ->", allocate_room("S5", "Vikram", "M", "2"))
    print("Occupants of A1:", rooms["A1"]["occupants"])
    vacate_room("S2")
    print("Occupants of A1 after S2 left:", rooms["A1"]["occupants"])
    print("Fee for S1, 45 days:", monthly_fee("S1", 45))
    print(
        "Priority (seniors first?):",
        [s["year"] for s in priority_order(
            [{"year": 1}, {"year": 4}, {"year": 2}]
        )]
    )
    print("Lottery:", room_lottery(["S6", "S7", "S8"]))
    print("Vacant beds:", vacant_beds())
    print("Warden DB:", connect_warden_db())
    print("Waitlist:", waitlist)


main()
