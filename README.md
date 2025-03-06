# Odoo Meeting Manager

## 📌 Overview
This French Odoo 17 module allows businesses and companies to plan, organize, and manage meetings efficiently. It provides comprehensive meeting lifecycle management with room allocation, departmental filtering, participant management, and seamless integration with the Odoo calendar.

## 🛠️ Features

### Meeting Management
- ✅ Create, update, and delete meetings
- ✅ Manage meeting states: Draft, Active, Cancelled, Done
- ✅ Associate meetings with departments
- ✅ Assign a responsible employee and participants
- ✅ Assign or book an in-person meeting in an available room for a specific time slot
- ✅ Automatically filter meetings by employee department
- ✅ Events are only created when a meeting is confirmed or completed
- ✅ Automatically update attendee list based on department participants

### Room Management
- ✅ Assign rooms to in-person meetings
- ✅ Prevent double booking of rooms
- ✅ Track room availability in real-time
- ✅ Filter available rooms based on capacity

### Calendar Integration
- ✅ Seamless integration with Odoo calendar module
- ✅ Calendar view menu item for easy visualization
- ✅ Automatic synchronization between meetings and calendar events
- ✅ Events update or delete when corresponding meetings change

### Filtering
- ✅ Search filters for efficient meeting discovery
- ✅ Department-based filtering
- ✅ Status-based filtering

## 👥 User Roles and Permissions

### Regular Users
- Can view only meetings that concern them
- Cannot create, modify or delete meeting rooms
- Cannot create, modify or delete meetings

### Administrators
- Can view all meetings regardless of state (draft, active, etc.)
- Can view meetings that concern them
- Full management capabilities for meetings and rooms

## 🔄 Workflow
1. Create a meeting and assign it to a department
2. Select participants from the department (with the ability to exclude specific employees)
3. When a meeting is confirmed, a calendar event is automatically created
4. Meeting states follow a logical progression: Draft → Active → Done (or Cancelled)
5. Room availability is checked in real-time to prevent scheduling conflicts
