from datetime import datetime, timedelta
from graph_database import conn 

def auto_schedule_tasks(target_date_str):
    try:
        work_start = datetime.strptime(f"{target_date_str} 09:00", "%Y-%m-%d %H:%M")
        work_end = datetime.strptime(f"{target_date_str} 18:00", "%Y-%m-%d %H:%M")

        events = []
        try:
            event_query = f"MATCH (e:Event) WHERE e.event_date = '{target_date_str}' RETURN e.start_time, e.end_time"
            e_result = conn.execute(event_query)
            while e_result.has_next():
                row = e_result.get_next()
                events.append({'start_time': row[0], 'end_time': row[1]})
        except Exception:
            pass 
            
        events = sorted(events, key=lambda e: datetime.strptime(e['start_time'], "%H:%M").time())

        pending_tasks = []
        task_query = "MATCH (t:Task) WHERE t.status = 'pending' RETURN t.title, t.duration_minutes, t.priority"
        t_result = conn.execute(task_query)
        
        while t_result.has_next():
            row = t_result.get_next()
            pending_tasks.append({
                'title': row[0],
                'duration_minutes': row[1],
                'priority': row[2]
            })
        
        if not pending_tasks:
            return "عذراً، لم أجد أي مهام قيد الانتظار (pending) لجدولتها اليوم. الرجاء إضافة مهام أولاً."

        priority_weight = {"High": 1, "Medium": 2, "Low": 3}
        pending_tasks = sorted(pending_tasks, key=lambda t: priority_weight.get(str(t['priority']).capitalize(), 4))

        current_time = work_start
        scheduled_count = 0
        
        for task in pending_tasks:
            task_duration = timedelta(minutes=int(task['duration_minutes']))
            is_scheduled = False
            
            while current_time + task_duration <= work_end:
                slot_end = current_time + task_duration
                has_conflict = False
                
                for event in events:
                    event_start = datetime.strptime(f"{target_date_str} {event['start_time']}", "%Y-%m-%d %H:%M")
                    event_end = datetime.strptime(f"{target_date_str} {event['end_time']}", "%Y-%m-%d %H:%M")
                    
                    if current_time < event_end and slot_end > event_start:
                        has_conflict = True
                        current_time = event_end
                        break     
                
                if not has_conflict:
                    start_str = current_time.strftime("%H:%M")
                    end_str = slot_end.strftime("%H:%M")
                    
                    update_query = """
                    MATCH (t:Task {title: $title}) 
                    SET t.status = 'scheduled', 
                        t.scheduled_date = $sch_date, 
                        t.scheduled_start = $sch_start, 
                        t.scheduled_end = $sch_end
                    """
                    
                    conn.execute(update_query, {
                        "title": task['title'],
                        "sch_date": target_date_str,
                        "sch_start": start_str,
                        "sch_end": end_str
                    })
                    
                    is_scheduled = True
                    scheduled_count += 1
                    current_time = slot_end
                    break 
            
        return f"تمت جدولة {scheduled_count} مهام بنجاح ليوم {target_date_str}. سيظهر الجدول الآن في التقويم."
        
    except Exception as e:
        return f"حدث خطأ داخلي أثناء الجدولة: {str(e)}"