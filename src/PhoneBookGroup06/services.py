# services.py
import os
import re

# --- SYSTEM PATH CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONTACT_FILE = os.path.join(DATA_DIR, "contacts.txt")
GROUP_FILE = os.path.join(DATA_DIR, "groups.txt")
RELATION_FILE = os.path.join(DATA_DIR, "contact_group.txt")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

from models import Contact, Group

class PhoneBookService:
    def __init__(self):
        self.contacts = []
        self.groups = []
        self.relations = [] 
        self.load_system_data()

    # --- HELPER: DATA PERSISTENCE ---
    def load_system_data(self):
        self.contacts.clear(); self.groups.clear(); self.relations.clear()
        
        if os.path.exists(CONTACT_FILE):
            with open(CONTACT_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) >= 3:
                        c = Contact(int(p[0]), p[1], p[2], p[3], p[4], p[5], p[6]=="True", p[7])
                        self.contacts.append(c)
        
        if os.path.exists(GROUP_FILE):
            with open(GROUP_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) >= 2:
                        self.groups.append(Group(int(p[0]), p[1], p[2] if len(p)>2 else ""))
        
        if os.path.exists(RELATION_FILE):
             with open(RELATION_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    p = line.strip().split("|")
                    if len(p) == 2:
                        self.relations.append((int(p[0]), int(p[1])))

    def save_system_data(self):
        with open(CONTACT_FILE, "w", encoding="utf-8") as f:
            for c in self.contacts:
                f.write(f"{c.contact_id}|{c.full_name}|{c.phone_number}|{c.email}|{c.address}|{c.note}|{c.is_favorite}|{c.created_at}\n")
        with open(GROUP_FILE, "w", encoding="utf-8") as f:
            for g in self.groups:
                f.write(f"{g.group_id}|{g.group_name}|{g.description}\n")
        with open(RELATION_FILE, "w", encoding="utf-8") as f:
            for r in self.relations:
                f.write(f"{r[0]}|{r[1]}\n")

    # --- VALIDATION HELPER ---
    def is_valid_email(self, email):
        if not email: return True
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    # --- CONTACT FEATURES ---
    def get_all_contacts(self, sort_by='id'):
        data = self.contacts[:]
        
        # Helper to get the last name for sorting (e.g. "Nguyen Van A" -> "a")
        def get_name_key(contact):
            if not contact.full_name: return ""
            return contact.full_name.strip().split(" ")[-1].lower()

        if sort_by == 'name_asc':
            data.sort(key=get_name_key)
        elif sort_by == 'name_desc':
            data.sort(key=get_name_key, reverse=True)
        else:
            data.sort(key=lambda x: x.contact_id)
        return data

    def get_contact_by_id(self, c_id):
        for c in self.contacts:
            if c.contact_id == c_id: return c
        return None

    def add_contact(self, full_name, phone, email, address, note):
        if not phone: return False, "Error: Phone number is required."
        for c in self.contacts:
            if c.phone_number == phone:
                return False, "Error: Phone number already exists."
        
        if not self.is_valid_email(email):
            return False, "Error: Invalid email format."

        new_id = 1 if not self.contacts else max(c.contact_id for c in self.contacts) + 1
        self.contacts.append(Contact(new_id, full_name, phone, email, address, note))
        self.save_system_data()
        return True, "Success: Contact added."

    def update_contact(self, c_id, name, phone, email, address, note):
        c = self.get_contact_by_id(c_id)
        if not c: return False, "Error: Contact not found."
        
        if phone and phone != c.phone_number:
            for existing in self.contacts:
                if existing.phone_number == phone:
                    return False, "Error: New phone number is already taken."
        
        if email and not self.is_valid_email(email):
            return False, "Error: Invalid email format."

        if name: c.full_name = name
        if phone: c.phone_number = phone
        if email: c.email = email
        if address: c.address = address
        if note: c.note = note
        self.save_system_data()
        return True, "Success: Contact updated."

    def delete_contact(self, c_id):
        c = self.get_contact_by_id(c_id)
        if c:
            self.contacts.remove(c)
            self.relations = [r for r in self.relations if r[0] != c_id]
            self.save_system_data()
            return True
        return False

    def toggle_favorite(self, c_id):
        c = self.get_contact_by_id(c_id)
        if c:
            c.is_favorite = not c.is_favorite
            self.save_system_data()
            return True, "Success: Favorite status updated."
        return False, "Error: Contact not found."

    def search_contact(self, keyword):
        kw = keyword.lower()
        return [c for c in self.contacts if kw in c.full_name.lower() or kw in c.phone_number or kw in c.email.lower()]

    # --- GROUP FEATURES ---
    def get_all_groups(self):
        return self.groups

    def get_group_by_id(self, g_id):
        for g in self.groups:
            if g.group_id == g_id: return g
        return None

    def create_group(self, name, desc):
        if not name: return False, "Error: Group name is required."
        for g in self.groups:
            if g.group_name.lower() == name.lower():
                return False, "Error: Group name already exists."
        new_id = 1 if not self.groups else max(g.group_id for g in self.groups) + 1
        self.groups.append(Group(new_id, name, desc))
        self.save_system_data()
        return True, "Success: Group created."

    def update_group(self, g_id, new_name, new_desc):
        g = self.get_group_by_id(g_id)
        if not g: return False, "Error: Group not found."
        
        if new_name and new_name.lower() != g.group_name.lower():
            for existing in self.groups:
                if existing.group_name.lower() == new_name.lower():
                    return False, "Error: Group name already exists."
            g.group_name = new_name
            
        if new_desc: g.description = new_desc
        self.save_system_data()
        return True, "Success: Group updated."

    def delete_group(self, g_id):
        g = self.get_group_by_id(g_id)
        if g:
            self.groups.remove(g)
            self.relations = [r for r in self.relations if r[1] != g_id]
            self.save_system_data()
            return True, "Success: Group deleted."
        return False, "Error: Group not found."

    # --- RELATIONSHIP FEATURES ---
    def get_groups_of_contact(self, c_id):
        group_ids = [r[1] for r in self.relations if r[0] == c_id]
        return [g for g in self.groups if g.group_id in group_ids]

    def get_contacts_in_group(self, g_id):
        contact_ids = [r[0] for r in self.relations if r[1] == g_id]
        return [c for c in self.contacts if c.contact_id in contact_ids]

    def assign_contact_to_group(self, c_id, g_id):
        if (c_id, g_id) not in self.relations:
            self.relations.append((c_id, g_id))
            self.save_system_data()
            return True, "Success: Assigned to group."
        return False, "Error: Already in this group."

    def remove_contact_from_group(self, c_id, g_id):
        if (c_id, g_id) in self.relations:
            self.relations.remove((c_id, g_id))
            self.save_system_data()
            return True, "Success: Removed from group."
        return False, "Error: Relation not found."

    # --- IMPORT / EXPORT ---
    def export_contacts_to_file(self, file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("ID|FullName|Phone|Email|Address|Note|Favorite|CreatedAt\n")
                for c in self.contacts:
                    f.write(f"{c.contact_id}|{c.full_name}|{c.phone_number}|{c.email}|{c.address}|{c.note}|{c.is_favorite}|{c.created_at}\n")
            return True, f"Success: Exported {len(self.contacts)} contacts."
        except Exception as e:
            return False, f"Error: {str(e)}"

    def import_contacts_from_file(self, file_path):
        if not os.path.exists(file_path):
            return False, "Error: File not found."
        
        count = 0
        skipped = 0
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if lines and "ID|" in lines[0]:
                    lines = lines[1:]
                
                for line in lines:
                    p = line.strip().split("|")
                    if len(p) < 3: continue
                    
                    phone = p[2]
                    is_dup = False
                    for c in self.contacts:
                        if c.phone_number == phone:
                            is_dup = True; break
                    
                    if is_dup:
                        skipped += 1
                    else:
                        self.add_contact(p[1], p[2], p[3] if len(p)>3 else "", "", "")
                        count += 1
            return True, f"Success: Imported {count} contacts. Skipped {skipped} duplicates."
        except Exception as e:
            return False, f"Error: {str(e)}"