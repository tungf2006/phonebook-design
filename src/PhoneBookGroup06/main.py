# main.py
import os
import time
from services import PhoneBookService

service = PhoneBookService()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("="*50)
    print(f"   {title.upper()}")
    print("="*50)

def input_str(prompt, current_val=None):
    if current_val:
        val = input(f"{prompt} [{current_val}]: ").strip()
        return val if val else current_val
    return input(f"{prompt}: ").strip()

# --- UI FUNCTIONS (ENGLISH) ---

def ui_contact_detail(c_id):
    while True:
        clear_screen()
        c = service.get_contact_by_id(c_id)
        if not c:
            print(">> Error: Contact not found (might be deleted).")
            time.sleep(1.5); break
        
        my_groups = service.get_groups_of_contact(c_id)
        group_names = ", ".join([g.group_name for g in my_groups]) if my_groups else "(None)"

        print_header("Contact Detail")
        print(f"ID:           {c.contact_id}")
        print(f"Full Name:    {c.full_name}")
        print(f"Phone:        {c.phone_number}")
        print(f"Email:        {c.email}")
        print(f"Address:      {c.address}")
        print(f"Groups:       {group_names}")
        print(f"Favorite:     {'Yes [*]' if c.is_favorite else 'No [ ]'}")
        print(f"Created At:   {c.created_at}")
        print("-" * 50)
        print("[U] Update Info")
        print("[D] Delete Contact")
        print("[F] Toggle Favorite")
        print("[G] Assign to Group")
        print("[R] Remove from Group") 
        print("[B] Back")
        
        choice = input("Choose action: ").upper()
        
        if choice == 'B': 
            break
        elif choice == 'F':
            service.toggle_favorite(c_id)
        elif choice == 'D':
            if input("Are you sure you want to delete? (Y/N): ").lower() == 'y':
                service.delete_contact(c_id)
                print(">> Contact deleted successfully.")
                time.sleep(1); break
        elif choice == 'U':
            ui_update_contact(c)
        elif choice == 'G':
            ui_assign_group(c)
        elif choice == 'R':
            ui_remove_from_group(c)

def ui_update_contact(c):
    clear_screen()
    print_header("UPDATE CONTACT")
    print("(Leave blank and press Enter to keep current value)\n")
    
    name = input_str("Full Name", c.full_name)
    phone = input_str("Phone", c.phone_number)
    email = input_str("Email", c.email)
    addr = input_str("Address", c.address)
    note = input_str("Note", c.note)
    
    success, msg = service.update_contact(c.contact_id, name, phone, email, addr, note)
    print(f"\n>> {msg}")
    input("Press Enter to return...") 

def ui_assign_group(c):
    clear_screen()
    print_header("ASSIGN TO GROUP")
    
    groups = service.get_all_groups()
    if not groups:
        print(">> No groups available. Please create a group first.")
        input("Press Enter to return..."); return

    print(f"{'ID':<5} | {'Group Name':<20}")
    print("-" * 30)
    for g in groups:
        print(f"{g.group_id:<5} | {g.group_name:<20}")
    print("-" * 30)
    
    try:
        g_id = int(input("\nEnter Group ID to assign: "))
        success, msg = service.assign_contact_to_group(c.contact_id, g_id)
        print(f">> {msg}")
    except ValueError:
        print(">> Error: Invalid ID format.")
    
    input("Press Enter to return...")

def ui_remove_from_group(c):
    clear_screen()
    print_header("REMOVE FROM GROUP")
    
    my_groups = service.get_groups_of_contact(c.contact_id)
    if not my_groups: 
        print(">> This contact is not in any group.")
        input("Press Enter to return..."); return
    
    print(f"{'ID':<5} | {'Group Name':<20}")
    print("-" * 30)
    for g in my_groups:
        print(f"{g.group_id:<5} | {g.group_name:<20}")
    print("-" * 30)

    try:
        g_id = int(input("\nEnter Group ID to remove: "))
        success, msg = service.remove_contact_from_group(c.contact_id, g_id)
        print(f">> {msg}")
    except ValueError:
        print(">> Error: Invalid ID format.")
    
    input("Press Enter to return...")

def view_contacts_ui():
    current_sort = 'id'
    sort_label = "ID (Default)"
    notification = "" 

    while True:
        clear_screen()
        print_header(f"CONTACT LIST (Current: {sort_label})")
        
        # --- PHẦN HIỂN THỊ NOTE ---
        if notification:
            print(f">> NOTE: {notification}")
            print("=" * 50)
            notification = "" 
        # --------------------------
        
        contacts = service.get_all_contacts(sort_by=current_sort)
        if not contacts: 
            print(">> No contacts found in system.")
        else:
            print(f"{'ID':<5} | {'Full Name':<25} | {'Phone':<12} | {'Fav'}")
            print("-" * 55)
            for c in contacts: print(c)
            print("-" * 55)
            
        # --- LOGIC XÁC ĐỊNH HÀNH ĐỘNG TIẾP THEO CỦA NÚT S ---
        if current_sort == 'id':
            next_sort_msg = "Sort Name A-Z"
        elif current_sort == 'name_asc':
            next_sort_msg = "Sort Name Z-A"
        else:
            next_sort_msg = "Reset to Default (ID)"
        # ---------------------------------------------------

        # --- MENU GỘP CHUNG (GỌN HƠN) ---
        print("\n--- MENU COMMANDS ---")
        print("[Number] Enter ID to View Detail")
        print("[A]      Add New Contact")
        print("[F]      Find / Search")
        print(f"[S]      {next_sort_msg}")  # Dòng S nằm chung nhóm
        print("[M]      Back to Main Menu")
        print("-" * 30)
        
        choice = input("Choice: ").strip().upper()
        
        if choice == 'M': break
        elif choice == 'A': 
            add_contact_ui()
        elif choice == 'F': 
            search_ui()
        elif choice == 'S':
            # Logic đổi trạng thái sắp xếp
            if current_sort == 'id': 
                current_sort = 'name_asc'
                sort_label = "Name (A-Z)"
                notification = "List is now sorted A - Z (Alex -> Bob)"
            elif current_sort == 'name_asc': 
                current_sort = 'name_desc'
                sort_label = "Name (Z-A)"
                notification = "List is now sorted Z - A (Bob -> Alex)"
            else: 
                current_sort = 'id'
                sort_label = "ID (Default)"
                notification = "List reset to Default (Oldest -> Newest)"
                
        elif choice.isdigit(): 
            ui_contact_detail(int(choice))

def add_contact_ui():
    clear_screen()
    print_header("ADD NEW CONTACT")
    
    name = input("Enter Full Name (Req): ").strip()
    phone = input("Enter Phone (Req): ").strip()
    
    if not name or not phone:
        print("\n>> Error: Name and Phone are required!")
        input("Press Enter to return..."); return
    
    email = input("Email: ").strip()
    address = input("Address: ").strip()
    note = input("Note: ").strip()
    
    success, msg = service.add_contact(name, phone, email, address, note)
    print(f"\n>> {msg}")
    input("Press Enter to return...")

def search_ui():
    while True:
        clear_screen()
        print_header("SEARCH CONTACT")
        print("Enter keyword to search (Name/Phone/Email)")
        print("(Leave blank and press Enter to go back)")
        
        kw = input("Keyword: ").strip()
        if not kw: break
        
        results = service.search_contact(kw)
        print(f"\nFound {len(results)} result(s):")
        if results:
            print(f"{'ID':<5} | {'Full Name':<25} | {'Phone':<12}")
            print("-" * 50)
            for c in results:
                print(f"{c.contact_id:<5} | {c.full_name:<25} | {c.phone_number:<12}")
            
            choice = input("\n[ID] View Detail or [Enter] New Search: ")
            if choice.isdigit():
                ui_contact_detail(int(choice))
        else:
            input("\nNo results found. Press Enter to try again...")

def manage_groups_ui():
    while True:
        clear_screen()
        print_header("MANAGE GROUPS")
        print("[1] View All Groups")
        print("[2] Create New Group")
        print("[3] Edit Group Name")
        print("[4] Delete Group")
        print("[5] View Contacts in Group (Filter)")
        print("[0] Back to Main Menu")
        
        choice = input("Choice: ")
        
        if choice == '1':
            clear_screen()
            print_header("GROUP LIST")
            groups = service.get_all_groups()
            if not groups: print(">> No groups found.")
            else: 
                for g in groups: print(g)
            input("\nPress Enter to return...")
            
        elif choice == '2':
            clear_screen()
            print_header("CREATE GROUP")
            success, msg = service.create_group(input("Name: "), input("Desc: "))
            print(f">> {msg}")
            input("Press Enter to return...")
            
        elif choice == '3':
            clear_screen()
            print_header("EDIT GROUP")
            for g in service.get_all_groups(): print(g)
            print("-" * 30)
            try:
                gid = int(input("Enter Group ID to Edit: "))
                new_name = input("New Name: ")
                desc = input("New Desc: ")
                success, msg = service.update_group(gid, new_name, desc)
                print(f">> {msg}")
            except ValueError: print(">> Error: Invalid Input")
            input("Press Enter to return...")
            
        elif choice == '4':
            clear_screen()
            print_header("DELETE GROUP")
            for g in service.get_all_groups(): print(g)
            print("-" * 30)
            try:
                gid = int(input("Enter Group ID to DELETE: "))
                if input("Confirm deletion? (Y/N): ").lower() == 'y':
                    success, msg = service.delete_group(gid)
                    print(f">> {msg}")
            except ValueError: print(">> Error: Invalid ID")
            input("Press Enter to return...")
            
        elif choice == '5':
            clear_screen()
            print_header("FILTER BY GROUP")
            groups = service.get_all_groups()
            if not groups:
                print(">> No groups available.")
            else:
                for g in groups: print(g)
                print("-" * 30)
                try:
                    gid = int(input("Enter Group ID: "))
                    members = service.get_contacts_in_group(gid)
                    
                    print(f"\n--- Members of Group ID {gid} ---")
                    if not members:
                        print(">> This group is empty.")
                    else:
                        print(f"{'ID':<5} | {'Full Name':<20} | {'Phone':<12}")
                        print("-" * 50)
                        for c in members:
                            print(f"{c.contact_id:<5} | {c.full_name:<20} | {c.phone_number:<12}")
                except ValueError:
                    print(">> Error: Invalid ID")
            input("\nPress Enter to return...")
                
        elif choice == '0': break

def import_export_ui():
    while True:
        clear_screen()
        print_header("IMPORT / EXPORT")
        print("[1] Import from TXT file")
        print("[2] Export to TXT file")
        print("[0] Back")
        
        choice = input("Choice: ")
        
        if choice == '1':
            clear_screen()
            print_header("IMPORT DATA")
            path = input("Enter file path (e.g. data/contacts.txt): ")
            print(">> Processing...")
            success, msg = service.import_contacts_from_file(path)
            print(f">> {msg}")
            input("Press Enter to return...")
            
        elif choice == '2':
            clear_screen()
            print_header("EXPORT DATA")
            path = input("Enter destination path (e.g. data/backup.txt): ")
            success, msg = service.export_contacts_to_file(path)
            print(f">> {msg}")
            input("Press Enter to return...")
            
        elif choice == '0': break

def main_menu():
    while True:
        clear_screen()
        print("=============================================")
        print("      PHONE BOOK MANAGEMENT SYSTEM (G06)")
        print("=============================================")
        print("[1] View Contact List")
        print("[2] Add New Contact")
        print("[3] Manage Groups")
        print("[4] Search Contact")
        print("[5] Import/Export")
        print("[0] Exit")
        print("=============================================")
        
        choice = input("Enter your choice: ")
        
        if choice == '1': view_contacts_ui()
        elif choice == '2': add_contact_ui()
        elif choice == '3': manage_groups_ui()
        elif choice == '4': search_ui()
        elif choice == '5': import_export_ui()
        elif choice == '0': 
            print("Goodbye!"); break
        else:
            print(">> Invalid choice! Try again.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"\n!!!! PROGRAM CRASHED !!!!")
        print(f"Error details: {e}")
        input("\nPress Enter to exit...")