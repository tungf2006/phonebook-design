# models.py
from datetime import datetime

class Contact:
    def __init__(self, contact_id, full_name, phone_number, email="", address="", note="", is_favorite=False, created_at=None):
        self.contact_id = contact_id
        self.full_name = full_name
        self.phone_number = phone_number
        self.email = email
        self.address = address
        self.note = note
        self.is_favorite = is_favorite # [cite: 243]
        
        # Tự động gán thời gian nếu không có
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        fav_str = "[*]" if self.is_favorite else "[ ]"
        return f"{self.contact_id:<5} | {self.full_name:<20} | {self.phone_number:<12} | {fav_str}"

class Group:
    def __init__(self, group_id, group_name, description=""):
        self.group_id = group_id
        self.group_name = group_name
        self.description = description # [cite: 251]

    def __str__(self):
        return f"{self.group_id:<5} | {self.group_name:<20} | {self.description}"