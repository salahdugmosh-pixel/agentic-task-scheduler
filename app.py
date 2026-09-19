from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta
from graph_database import conn
from graph_database import db
from llm_agent import chat_with_data
from scheduler import auto_schedule_tasks

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    ai_response = chat_with_data(user_message)
    return jsonify({"reply": ai_response})

@app.route("/auto_schedule", methods=["POST"])
def auto_schedule():
    today = datetime.now().strftime("%Y-%m-%d")
    auto_schedule_tasks(today)
    return redirect(url_for("home"))

@app.route("/api/tasks")
def get_calendar_tasks():
    query = "MATCH (t:Task) WHERE t.scheduled_start IS NOT NULL RETURN t.title, t.scheduled_start, t.duration_minutes, t.priority"
    result = conn.execute(query)
    
    events = []
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    while result.has_next():
        row = result.get_next()
        title = row[0]
        start_time_str = row[1] 
        duration = row[2]       
        priority = row[3]       
        
        try:
            start_dt = datetime.strptime(f"{today_str} {start_time_str}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=int(duration))
            
            if priority.lower() == "high":
                color = "#DC2626" 
            elif priority.lower() == "medium":
                color = "#D97706" 
            else:
                color = "#059669" 
                
            events.append({
                "title": title,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
                "backgroundColor": color,
                "borderColor": color
            })
        except Exception as e:
            print(f"Error parsing date for task {title}: {e}")
            continue
            
    return jsonify(events)
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)