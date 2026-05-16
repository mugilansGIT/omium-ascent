import asyncio
from app.database import get_supabase
import uuid

async def seed():
    supabase = get_supabase()
    print("Seeding data...")

    # 1. Get Departments
    deps = supabase.table("departments").select("*").execute()
    if not deps.data:
        print("No departments found. Please run setup_db.sql first.")
        return
    
    dept_map = {d["name"]: d["id"] for d in deps.data}
    
    # 2. Create a demo admin employee (the one our bypassed auth will use)
    admin_id = "00000000-0000-0000-0000-000000000000"
    admin_data = {
        "full_name": "System Admin",
        "email": "admin@example.com",
        "role": "admin",
        "designation": "Operations Director",
        "department_id": dept_map.get("Management"),
        "status": "active"
    }
    
    # Check if exists
    existing = supabase.table("employees").select("*").eq("email", admin_data["email"]).execute()
    if not existing.data:
        admin = supabase.table("employees").insert(admin_data).execute().data[0]
        admin_uuid = admin["id"]
        print(f"Created Admin: {admin['full_name']}")
    else:
        admin_uuid = existing.data[0]["id"]
        print(f"ℹ️ Admin already exists")

    # 3. Create some teammates
    teammates = [
        {"full_name": "Sarah Connor", "email": "sarah@example.com", "role": "employee", "designation": "Senior Engineer", "department_id": dept_map.get("Engineering")},
        {"full_name": "John Doe", "email": "john@example.com", "role": "employee", "designation": "HR Manager", "department_id": dept_map.get("HR")},
    ]
    
    for t in teammates:
        if not supabase.table("employees").select("*").eq("email", t["email"]).execute().data:
            supabase.table("employees").insert(t).execute()
            print(f"Created Employee: {t['full_name']}")

    # 4. Create some tasks
    tasks = [
        {"title": "Review Q2 Budget", "description": "AI needs to verify department spends", "assigned_to": admin_uuid, "priority": "high", "status": "todo"},
        {"title": "Onboard new agents", "description": "Configure Redis stream listeners", "assigned_to": admin_uuid, "priority": "medium", "status": "in_progress"},
        {"title": "Fix server lag", "description": "Optimize database queries", "priority": "low", "status": "todo"},
    ]
    
    for task in tasks:
        if not supabase.table("tasks").select("*").eq("title", task["title"]).execute().data:
            supabase.table("tasks").insert(task).execute()
            print(f"Created Task: {task['title']}")

    # 5. Create some vendors
    vendors = [
        {"name": "CloudCorp", "category": "Infrastructure", "rating": 4.5, "status": "active"},
        {"name": "OfficeSupply Co", "category": "Procurement", "rating": 3.8, "status": "active"},
    ]
    
    for v in vendors:
        if not supabase.table("vendors").select("*").eq("name", v["name"]).execute().data:
            supabase.table("vendors").insert(v).execute()
            print(f"Created Vendor: {v['name']}")

    print("Seeding complete! Refresh your dashboard.")

if __name__ == "__main__":
    asyncio.run(seed())
