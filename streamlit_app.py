import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import uuid
import random

st.set_page_config(page_title="Smart Task Manager", layout="wide")

# CSS styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Comic+Neue:wght@400;700&display=swap');

    .stApp {
        background-color: #fff7ed;
        font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif;
        color: #cc6600;
    }
    h1, h2, h3 {
        font-weight: 700;
        color: #cc6600 !important;
    }
    div.stButton > button {
        background-color: #ffb366;
        color: #994d00;
        border: none;
        border-radius: 20px;
        padding: 0.6em 1.4em;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 2px 2px 8px rgba(255, 153, 51, 0.3);
        cursor: pointer;
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #e69900;
        color: white;
        box-shadow: 4px 4px 14px rgba(230, 153, 0, 0.6);
    }
    .add-task-btn-container > button {
        background-color: #ffefdb !important;
        color: #994d00 !important;
        border: 2px solid #ffb366 !important;
        border-radius: 20px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.5em 1.5em !important;
        box-shadow: 2px 2px 8px rgba(255, 153, 51, 0.25) !important;
    }
    div.stTextInput > div > input,
    div.stNumberInput > div > input,
    div.stTimeInput > div > input {
        background-color: #ffe6cc;
        color: #cc6600 !important;
        border: 2px solid #ffb366;
        border-radius: 15px;
        padding: 0.6em 0.8em;
        font-weight: 600;
        font-size: 1rem;
        font-family: 'Comic Neue', 'Comic Sans MS', cursive, sans-serif;
    }
    .add-task-section {
        background-color: white;
        padding: 2rem 2.5rem;
        border-radius: 25px;
        box-shadow: 0 4px 15px rgba(255, 153, 51, 0.25);
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# App title
st.markdown('<h1>Smart Task Manager</h1>', unsafe_allow_html=True)

# Initialize session state for tasks
if "tasks" not in st.session_state:
    st.session_state.tasks = []

STICKY_NOTE_COLORS = [
    "#d0f0f4", "#d8eafd", "#f0d9ff", "#d5fdd5", "#fffacd",
    "#fce3ec", "#e6f7ff", "#e0f7fa", "#f5f5dc", "#e1f0d7",
]

# Sticky Note Board with checkboxes directly under each note
st.markdown('<h3>✎ Sticky Note Board</h3>', unsafe_allow_html=True)
tasks = sorted(st.session_state.tasks, key=lambda x: x["start"])

if tasks:
    cols = st.columns(3)
    for i, task in enumerate(tasks):
        if "color" not in task:
            task["color"] = random.choice(STICKY_NOTE_COLORS)
        if "completed" not in task:
            task["completed"] = False

        with cols[i % 3]:
            # Checkbox for this task
            current = st.checkbox("Done", key=f"check_{task['id']}", value=task["completed"])
            task["completed"] = current
            task["timeline_color"] = "#d3d3d3" if current else task["color"]

            # Sticky note below the checkbox with minimal margin top to reduce gap
            bg_color = task["timeline_color"]
            st.markdown(
                f"""
                <div style='
                    background-color: {bg_color};
                    padding: 1.2em;
                    margin: 0.1em 0 0.5em 0;
                    font-size: 16px;
                    border-radius: 20px;
                    box-shadow: 4px 4px 10px rgba(200, 200, 200, 0.3);
                '>
                    <strong>{task['title']}</strong><br>
                    {task['start'].strftime('%H:%M')} - {task['end'].strftime('%H:%M')}
                </div>
                """,
                unsafe_allow_html=True,
            )
else:
    st.info("No tasks available.")

# Timeline Chart
st.markdown('<h3>■ Timeline View</h3>', unsafe_allow_html=True)
if tasks:
    df = pd.DataFrame(tasks)
    df["Task"] = df["title"]
    df["Start"] = df["start"]
    df["Finish"] = df["end"]
    df["Color"] = df["timeline_color"]

    fig = px.timeline(
        df, x_start="Start", x_end="Finish", y="Task", color="Color", color_discrete_map="identity"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(
        tickformat="%H:%M",
        side="top",
        tickfont=dict(color="black", size=14, family="Comic Neue"),
        title_font=dict(color="black", size=16),
    )
    fig.update_layout(
        font=dict(family="Comic Neue", size=14, color="black"),
        xaxis_title="Time",
        yaxis_title="Tasks",
        height=420,
        showlegend=False,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffe0b3",
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No tasks scheduled.")

# Add Task Section
st.markdown('<div class="add-task-section">', unsafe_allow_html=True)
st.markdown('<h2>▶ Add New Task</h2>', unsafe_allow_html=True)

with st.form("simple_task_form", clear_on_submit=True):
    task_name = st.text_input("Task Name")
    start_time = st.time_input("Task Start Time")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=1440, step=15)

    st.markdown('<div class="add-task-btn-container">', unsafe_allow_html=True)
    submitted = st.form_submit_button("＋ Add Task")
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted and task_name:
        now = datetime.now()
        start_dt = datetime.combine(now.date(), start_time)
        end_dt = start_dt + timedelta(minutes=duration)
        color = random.choice(STICKY_NOTE_COLORS)
        new_task = {
            "id": str(uuid.uuid4()),
            "title": task_name,
            "start": start_dt,
            "end": end_dt,
            "color": color,
            "timeline_color": color,
            "completed": False,
        }
        st.session_state.tasks.append(new_task)
        st.success(f"Task '{task_name}' added!")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

