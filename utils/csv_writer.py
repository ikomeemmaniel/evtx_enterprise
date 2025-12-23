import csv

def write_events_to_csv(events, output_path):
    fieldnames = [
        'No.', 'Username', 'IP Address', 'EventID', 'Timestamp', 
        'Security ID', 'Action', 'Keywords', 'Failure Reason', 'ProcessName'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, event in enumerate(events, start=1):
            writer.writerow({
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
