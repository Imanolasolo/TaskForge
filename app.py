import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect('tasks.db')
c = conn.cursor()

# Create tasks table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, created_at TEXT, expiration_date TEXT, comment TEXT, duration_hours INTEGER, resolved BOOLEAN, executed BOOLEAN)''')
conn.commit()

# Function to add a new task
def add_task(task_name, comment, duration_hours):
    created_at = datetime.now()
    expiration_date = created_at + timedelta(hours=duration_hours)
    c.execute("INSERT INTO tasks (name, created_at, expiration_date, comment, duration_hours, resolved, executed) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (task_name, created_at, expiration_date, comment, duration_hours, False, False))
    conn.commit()

# Function to edit an existing task by ID
def edit_task(task_id, new_task_name, new_comment, new_duration_hours, resolved, executed):
    c.execute("UPDATE tasks SET name=?, comment=?, duration_hours=?, resolved=?, executed=? WHERE id=?",
              (new_task_name, new_comment, new_duration_hours, resolved, executed, task_id))
    conn.commit()

# Function to delete a task by ID
def delete_task(task_id):
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()

# Function to fetch all tasks from the database
def fetch_tasks():
    c.execute("SELECT * FROM tasks")
    return c.fetchall()

# Function to fetch task names and their resolved status from the database
def fetch_task_names_and_status():
    c.execute("SELECT name, resolved FROM tasks")
    return c.fetchall()

# User interface
col1, col2= st.columns([1,2])
with col1:
    st.markdown("<h1 style='color: red;'>TaskForge</h1>", unsafe_allow_html=True)
with col2:
    st.markdown("<h1 style='color: white;'>Task development app</h1>", unsafe_allow_html=True)

# Sidebar navigation menu
menu_selection = st.sidebar.radio("Navigation", ["Add Task", "Edit or Delete Tasks", "Task Status"])


# Page to add a new task
if menu_selection == "Add Task":
    st.subheader("Add New Task")
    task_input = st.text_input("Task Name:")
    comment_input = st.text_input("Comment:")
    duration_input = st.number_input("Task Duration (hours):", min_value=1)
    if st.button("Add Task"):
        if task_input:
            add_task(task_input, comment_input, duration_input)
            st.success("Task added successfully!")

# Task edition page
elif menu_selection == "Edit or Delete Tasks":
    st.subheader("Edit & Delete tasks")
    tasks = fetch_tasks()
    
    if tasks:
        task_names = [task[1] for task in tasks]
        selected_task_name = st.selectbox("Select Task to Edit:", task_names)
        selected_task_index = task_names.index(selected_task_name)
        selected_task = tasks[selected_task_index]

        if selected_task:
            st.info(f"Name: {selected_task[1]}")
            st.text(f"Created at: {selected_task[2]}")
            st.text(f"Comment: {selected_task[4]}")
            st.text(f"Duration: {selected_task[5]} hours")
            resolved = st.checkbox("Mark as Resolved", selected_task[6])
            executed = st.checkbox("Mark as Executed", selected_task[7])

            edited_task_name = st.text_input("Edit Task Name:", value=selected_task[1])
            edited_comment = st.text_input("Edit Comment:", value=selected_task[4])
            edited_duration_hours = st.number_input("Edit Task Duration (hours):", min_value=1, value=selected_task[5])

            if st.button("Save Changes"):
                edit_task(selected_task[0], edited_task_name, edited_comment, edited_duration_hours, resolved, executed)
                st.success("Task edited successfully!")
                st.rerun()
                
            if st.button("Delete Task"):
                delete_task(selected_task[0])
                st.success("Task deleted successfully!")
                st.rerun()
        else:
            st.write("No tasks selected.")
    else:
        st.write("No tasks available.")

# Page to show task status (resolved or not)
if menu_selection == "Task Status":
    st.subheader("Task Status")
    tasks = fetch_task_names_and_status()

    if tasks:
        st.write("Task Name | Resolved")
        st.write("--- | ---")
        for task in tasks:
            status_color = "red" if task[1] else "yellow"
            resolved_text = "<span style='color: {};'>{}</span>".format(status_color, "Yes" if task[1] else "No")
            st.write(f"{task[0]} | {resolved_text}", unsafe_allow_html=True)
    else:
        st.write("No tasks available.")

# Close the connection to the database when Streamlit app is closed
conn.close()



