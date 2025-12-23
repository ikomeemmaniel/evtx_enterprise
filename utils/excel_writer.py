import pandas as pd

def write_events_to_excel(events, output_path):
    data = []
    for i, event in enumerate(events, start=1):
        data.append({
            'No.': i,
            'Username': event.user_sid,
            'IP Address': event.ip_address,
            'EventID': event.event_id,
            'Timestamp': event.timestamp,
            'Security ID': event.security_id,
            'Action': event.action,
            'Keywords': event.keywords,
            'Failure Reason': event.failure_reason,
            'ProcessName': event.process_name
        })
    
    df = pd.DataFrame(data)
    cols = ['No.', 'Username', 'IP Address', 'EventID', 'Timestamp', 'Security ID', 'Action', 'Keywords', 'Failure Reason', 'ProcessName']
    df = df[cols]

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Forensic Analysis')
