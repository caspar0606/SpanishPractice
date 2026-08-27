from datetime import datetime, timezone
import uuid

def generate_id():
    return f"{datetime.now(timezone.utc).isoformat()}_{uuid.uuid4()}"
