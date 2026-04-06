from datetime import datetime
import uuid

def generate_id():
    return f"{datetime.utcnow().isoformat()}_{uuid.uuid4()}"