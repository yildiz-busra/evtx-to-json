import json
from lxml import etree
from Evtx.Evtx import Evtx
from Evtx.Views import evtx_file_xml_view

def sanitize_xml(xml_string):
    sanitized_xml = xml_string.replace('object=', 'object="undefined"=')
    return sanitized_xml

def strip_namespace(tag):
    """Strips the namespace from an XML tag."""
    if '}' in tag:
        return tag.split('}', 1)[1]
    else:
        return tag

def evtx_to_json(evtx_file_path, json_file_path):
    events = []

    with Evtx(evtx_file_path) as log:
        for record in log.records():
            try:
                xml_string = record.xml()
                sanitized_xml = sanitize_xml(xml_string)
                xml_root = etree.fromstring(sanitized_xml)
                
                event_dict = {}

                event_dict[strip_namespace(xml_root.tag)] = {strip_namespace(k): v for k, v in xml_root.attrib.items()}

                for child in xml_root:
                    child_dict = {}
                    if child.attrib:
                        child_dict.update({strip_namespace(k): v for k, v in child.attrib.items()})
                    if child.text and child.text.strip():
                        child_dict['text'] = child.text.strip()
                    
                    if child.tag.endswith('System') or child.tag.endswith('EventData'):
                        event_dict[strip_namespace(child.tag)] = {}
                        for subchild in child:
                            if subchild.tag.endswith('Data'):
                                event_dict[strip_namespace(child.tag)][strip_namespace(subchild.attrib['Name'])] = subchild.text
                            else:
                                event_dict[strip_namespace(child.tag)][strip_namespace(subchild.tag)] = subchild.text
                    else:
                        event_dict[strip_namespace(child.tag)] = child_dict or None

                events.append(event_dict)

            except etree.XMLSyntaxError as e:
                print(f"Failed to parse XML for a record: {e}")
                print(f"Problematic XML: {xml_string[:200]}...")  
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

    with open(json_file_path, 'w') as json_file:
        json.dump(events, json_file, indent=4)

if __name__ == "__main__":

    evtx_file_path = "/input_file" 
    json_file_path = "/output_file"
    evtx_to_json(evtx_file_path, json_file_path)
    print(f"Conversion complete. JSON output saved to {json_file_path}")


