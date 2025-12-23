from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view
from datetime import datetime
import xml.etree.ElementTree as ET

class ParsedEvent:
    def __init__(self, event_id, timestamp, **kwargs):
        self.event_id = event_id
        self.timestamp = timestamp
        self.user_sid = kwargs.get('user_sid')
        self.ip_address = kwargs.get('ip_address')
        self.security_id = kwargs.get('security_id')
        self.action = kwargs.get('action')
        self.keywords = kwargs.get('keywords')
        self.failure_reason = kwargs.get('failure_reason')
        self.process_name = kwargs.get('process_name')

def validate_evtx_file(path: str) -> bool:
    try:
        with Evtx(path): return True
    except: return False

def parse_evtx_file(path: str):
    events = []
    ns = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
    
    # Mapping for your specific forensic analysis requirements
    failure_map = {
        "0xc000006a": "Incorrect password",
        "0xc0000064": "User name does not exist",
        "0xc000006d": "Incorrect username or password",
        "0xc000015b": "Logon type not granted",
        "0xc0000234": "Account locked out",
        "0x0": "N/A"
    }

    try:
        with Evtx(path) as evtx:
            for xml_str, record in evtx_file_xml_view(evtx.get_file_header()):
                try:
                    root = ET.fromstring(xml_str)
                    system = root.find("ns:System", ns)
                    if system is None: continue

                    event_id = system.findtext("ns:EventID", namespaces=ns)
                    time_node = system.find("ns:TimeCreated", ns)
                    timestamp = datetime.fromisoformat(time_node.attrib.get("SystemTime").replace("Z", "+00:00")) if time_node is not None else None

                    data_map = {}
                    event_data = root.find("ns:EventData", ns)
                    if event_data is not None:
                        for data in event_data.findall("ns:Data", ns):
                            name = data.attrib.get("Name")
                            if name: data_map[name] = data.text

                    # Forensic Logic for Action and Failure Reason
                    raw_status = data_map.get("SubStatus") or data_map.get("Status") or "0x0"
                    action_text = "Audit Failure" if event_id == "4625" else "Audit Success" if event_id == "4624" else "Security Event"
                    
                    # Convert hex to human-readable as requested
                    reason_text = failure_map.get(raw_status.lower(), raw_status)

                    events.append(ParsedEvent(
                        event_id=event_id,
                        timestamp=timestamp,
                        user_sid=data_map.get("TargetUserName") or data_map.get("SubjectUserName") or "N/A",
                        ip_address=data_map.get("IpAddress") or data_map.get("SourceNetworkAddress") or "N/A",
                        security_id=data_map.get("TargetUserSid") or data_map.get("SubjectUserSid") or "N/A",
                        action=action_text,
                        keywords=system.findtext("ns:Keywords", namespaces=ns) or "N/A",
                        failure_reason=reason_text,
                        process_name=data_map.get("ProcessName") or data_map.get("CallerProcessName") or "N/A"
                    ))
                except: continue
    except Exception as e:
        print(f"Parser error: {e}")
    return events
