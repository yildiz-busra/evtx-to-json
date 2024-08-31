import json
from lxml import etree
from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view

def sanitize_xml(xml_string):
    # Example of sanitization: replacing any instances of attributes with no value with a placeholder value.
    sanitized_xml = xml_string.replace('object=', 'object="undefined"=')
    return sanitized_xml

def strip_namespace(tag):
    """Strips the namespace from an XML tag."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    else:
        return tag

def evtx_to_json(evtx_file_path, json_file_path):
    """
    Convert an .evtx file to a JSON file.

    :param evtx_file_path: Path to the .evtx file
    :param json_file_path: Path to the output JSON file
    """
    events = []

    with Evtx(evtx_file_path) as log:
        for record in log.records():
            try:
                # Convert the record to XML string
                xml_string = record.xml()
                # Sanitize the XML
                sanitized_xml = sanitize_xml(xml_string)
                # Parse the XML
                xml_root = etree.fromstring(sanitized_xml)
                
                # Convert the XML to a dictionary
                event_dict = {}

                # Strip namespace and convert attributes
                event_dict[strip_namespace(xml_root.tag)] = {strip_namespace(k): v for k, v in xml_root.attrib.items()}

                for child in xml_root:
                    child_dict = {}
                    if child.attrib:
                        child_dict.update({strip_namespace(k): v for k, v in child.attrib.items()})
                    if child.text and child.text.strip():
                        child_dict['text'] = child.text.strip()
                    
                    # Handle System and EventData separately
                    if child.tag.endswith('System') or child.tag.endswith('EventData'):
                        event_dict[strip_namespace(child.tag)] = {}
                        for subchild in child:
                            if subchild.tag.endswith('Data'):
                                event_dict[strip_namespace(child.tag)][strip_namespace(subchild.attrib['Name'])] = subchild.text
                            else:
                                event_dict[strip_namespace(child.tag)][strip_namespace(subchild.tag)] = subchild.text
                    else:
                        event_dict[strip_namespace(child.tag)] = child_dict or None

                # Add the event to the list
                events.append(event_dict)

            except etree.XMLSyntaxError as e:
                print(f"Failed to parse XML for a record: {e}")
                print(f"Problematic XML: {xml_string[:200]}...")  # Print first 200 chars for context
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

    # Write the list of events to the JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(events, json_file, indent=4)

if __name__ == "__main__":
    # Example usage
    evtx_file_path = "/home/kali/Desktop/lab/walkthrough/unit42Sherlock/Microsoft-Windows-Sysmon-Operational.evtx"
    json_file_path = "/home/kali/Desktop/lab/walkthrough/unit42Sherlock/output_file.json"
    evtx_to_json(evtx_file_path, json_file_path)
    print(f"Conversion complete. JSON output saved to {json_file_path}")


