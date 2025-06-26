import requests
import xml.etree.ElementTree as ET

def get_wfs_layer_attributes_simple(wfs_url, layer_name):
    """
    Fetches and parses DescribeFeatureType directly.
    Extracts attribute names from <xsd:element> inside <xsd:sequence>.
    Works when DescribeFeatureType inlines the type definition.
    """

    # Build DescribeFeatureType URL
    params = {
        'SERVICE': 'WFS',
        'REQUEST': 'DescribeFeatureType',
        'VERSION': '2.0.0',
        'TYPENAME': layer_name
    }
    full_url = requests.Request('GET', wfs_url, params=params).prepare().url
    # print(f"DescribeFeatureType URL: {full_url}")

    # Fetch it
    resp = requests.get(full_url)
    resp.raise_for_status()

    # Parse XML
    tree = ET.fromstring(resp.content)
    ns = {'xsd': 'http://www.w3.org/2001/XMLSchema'}

    # Find the element for the layer → get type
    local_name = layer_name.split(":")[-1]

    # Find the <xsd:element> for the layer
    type_name = None
    for el in tree.findall('.//xsd:element', ns):
        if el.attrib.get('name') == local_name:
            type_name = el.attrib.get('type')
            break

    if not type_name:
        # Fallback guess: local name + "Type"
        type_name = local_name + "Type"

    type_local = type_name.split(":")[-1]

    # Find the <xsd:complexType>
    complex_type = None
    for ct in tree.findall('.//xsd:complexType', ns):
        if ct.attrib.get('name') == type_local:
            complex_type = ct
            break

    if not complex_type:
        print(f"Could not find complexType '{type_local}' in DescribeFeatureType.")
        return []

    # Extract attribute names from <xsd:sequence>
    attributes = []
    sequence = complex_type.find('.//xsd:sequence', ns)
    if sequence is not None:
        for prop in sequence.findall('xsd:element', ns):
            attr_name = prop.attrib.get('name')
            if attr_name:
                attributes.append(attr_name)

    return attributes



import requests
import html2text
import re

def get_html_as_markdown(url, identifier):
    try:
        response = requests.get(url)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")

        if "text/html" not in content_type.lower():
            print(f"Error: URL did not return HTML. Content-Type is '{content_type}'")
            return None

        html_content = response.text  # Safe: we know it's text/html

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.ignore_emphasis = False
        h.body_width = 0

        markdown = h.handle(html_content)

        # Normalize multiple newlines to two
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Remove prefix if it starts with 'Technische Beschreibung\n\n \n\n'
        prefix_pattern = r'^Technische Beschreibung\s*\n\s*\n\s*'
        markdown = re.sub(prefix_pattern, '', markdown, count=1, flags=re.IGNORECASE)

        return markdown

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}. ID:{identifier}")
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}. ID:{identifier}")

    return None



from urllib.parse import urlparse, urlunparse

def strip_query(url):
    parsed = urlparse(url)
    stripped = parsed._replace(query="", fragment="")
    return urlunparse(stripped)


KEYWORDS_TO_REMOVE = {
    "berlin",
    "geodaten",
    "opendata",
    "open data",
    "karten",
    "umweltatlas",
    "infofeatureaccessservice",
    "infomapaccessservice",
    "features",
    "sachdaten"
}

def clean_keywords(keywords):
    """
    Remove unwanted keywords defined in KEYWORDS_TO_REMOVE from a list of keywords.
    Handles None values gracefully.
    """
    if not keywords:
        return []
    cleaned = []
    for key in keywords:
        if key is None:
            continue
        s = str(key).strip().lower()
        if s and s not in KEYWORDS_TO_REMOVE:
            cleaned.append(s)
    return cleaned





import requests
import xml.etree.ElementTree as ET

def get_attribute_descriptions_from_describe_featuretype(wfs_url: str, layer_name: str):
    """
    Safe version:
    - Never raises.
    - Returns {} if it fails.
    """
    attr_docs = {}

    try:
        params = {
            "SERVICE": "WFS",
            "REQUEST": "DescribeFeatureType",
            "VERSION": "2.0.0",
            "TYPENAME": layer_name
        }
        full_url = requests.Request("GET", wfs_url, params=params).prepare().url
        resp = requests.get(full_url)
        resp.raise_for_status()

        tree = ET.fromstring(resp.content)
        ns = {"xsd": "http://www.w3.org/2001/XMLSchema"}

        local_name = layer_name.split(":")[-1]
        type_name = None

        for el in tree.findall(".//xsd:element", ns):
            if el.get("name") == local_name:
                type_name = el.get("type")
                break

        if not type_name:
            type_name = local_name + "Type"
        type_local = type_name.split(":")[-1]

        complex_type = None
        for ct in tree.findall(".//xsd:complexType", ns):
            if ct.get("name") == type_local:
                complex_type = ct
                break

        if not complex_type:
            print('prop description could not be found for layer: ',layer_name)

            # Don’t break, just return empty
            return attr_docs

        sequence = complex_type.find(".//xsd:sequence", ns)
        if sequence is not None:
            for prop in sequence.findall("xsd:element", ns):
                name = prop.get("name")
                doc = ""
                annotation = prop.find("xsd:annotation/xsd:documentation", ns)
                if annotation is not None and annotation.text:
                    doc = annotation.text.strip()
                if name:
                    attr_docs[name] = doc

    except Exception:
        print('prop description could not be found for layer: ',layer_name)
        # Safe fallback: never break your main WFS logic
        pass

    return attr_docs


# a script to get old attribute descriptions

# import os
# import json

# # Paths
# base_dir = "../scraper/data/datasets/"
# ckan_file = "ckan.json"


# # Result dictionary
# result = {}

# # Loop through all folders in base_dir
# for folder_name in os.listdir(base_dir):
#     folder_path = os.path.join(base_dir, folder_name)
#     if os.path.isdir(folder_path):
#         attr_file = os.path.join(folder_path, "attributesDescription.json")
#         ckan_file = os.path.join(folder_path, "ckan.json")

#         if os.path.isfile(attr_file) and os.path.isfile(ckan_file):
#             try:
#                 # Load attributesDescription.json
#                 with open(attr_file, "r") as f:
#                     attributes = json.load(f)

#                 # Load ckan.json
#                 with open(ckan_file, "r") as f:
#                     ckan_data = json.load(f)

#                 # Check if attributesDescription.json is a non-empty array
#                 if isinstance(attributes, list) and attributes:
#                     guid = ckan_data.get("guid")
#                     if guid:
#                         result[guid] = attributes

#             except json.JSONDecodeError as e:
#                 print(f"Warning: JSON decode error in folder '{folder_name}': {e}")

# # Save the result to a JSON file
# with open("attributesDescription.json", "w") as f:
#     json.dump(result, f, indent=2, ensure_ascii=False)

# print("Done! Output written to output.json.")






# import json
# import os
# from datetime import datetime, timedelta

# # Replace with your actual JSON file name
# FILE_NAME = "../data/csw_records.json"
# BASE_DIR = "../datasets"

# # Open and load the JSON file
# with open(FILE_NAME, 'r') as file:
#     data = json.load(file)

# # Get today's date and 10 days ago
# today = datetime.now()
# ten_days_ago = today - timedelta(days=10)

# for obj in data:
#     identifier = obj.get('identifier', 'N/A')

#     # Replace 'modified' with your actual date field name
#     date_str = obj.get('modified', None)

#     # Check if modified date is within 10 days
#     if date_str:
#         try:
#             date_obj = datetime.fromisoformat(date_str)

#             if date_obj >= ten_days_ago:
#                 print(f"✅ Recent: {identifier} (Date: {date_str})")
#             else:
#                 print(f"⏭️ Older than 10 days: {identifier} (Date: {date_str})")

#         except ValueError:
#             print(f"⚠️ Could not parse date for {identifier}: {date_str}")
#     else:
#         print(f"❌ No date for {identifier}")

#     # === Check/create folder and write JSON ===
#     folder_path = os.path.join(BASE_DIR, identifier)

#     # Create folder if it doesn't exist
#     os.makedirs(folder_path, exist_ok=True)

#     # Define the file name to write
#     output_file = os.path.join(folder_path, "record.json")

#     # Always write (overwrite or update)
#     with open(output_file, 'w') as out_file:
#         json.dump(obj, out_file, indent=2)

#     print(f"📁 Saved object to {output_file}")








# import json
# from pathlib import Path
# from urllib.parse import urlparse, urlunparse
# from datetime import datetime, timedelta
# from pathlib import Path

# # CONFIG
# LAST_UPDATE = datetime.now() - timedelta(days=10)  # 1 day ago
# RUN_UPDATE = True  # Toggle update check

# def remove_last_part(string):
#     """Remove last dash-separated part from a string."""
#     if '-' in string:
#         return '-'.join(string.split('-')[:-1])
#     return string

# def remove_parameters_from_url(url):
#     """Remove query parameters from URL."""
#     parsed = urlparse(url)
#     cleaned = parsed._replace(query='')
#     return urlunparse(cleaned)

# def parse_ckan_data():
#     # Load CKAN data
#     ckan_data_file = "../data/ckan_data.json"
#     with open(ckan_data_file, encoding="utf-8") as f:
#         ckan_data = json.load(f)

#     updated_datasets = []

#     for item in ckan_data:
#         geo_resource = None
#         geo_data = {}

#         # Get only WFS and WMS resources
#         for resource in item.get('resources', []):
#             url = resource.get('url', '').lower()
#             format_ = resource.get('format', '').upper()

#             if (
#                 ("request=getcapabilities&service=wms" in url or
#                  "request=getcapabilities&service=wfs" in url)
#                 and format_ in ["WFS", "WMS"]
#             ):
#                 geo_resource = resource

#         if not geo_resource:
#             continue

#         # Check update/release date
#         update_date = datetime.fromisoformat(item['metadata_modified'])
#         after_update = update_date > LAST_UPDATE

#         release_date = datetime.fromisoformat(item.get('metadata_created'))
#         after_release = release_date > LAST_UPDATE and not item.get('metadata_modified')

#         if RUN_UPDATE and not (after_update or after_release):
#             continue

#         # Prepare geo_data
#         geo_data['title'] = item.get('title')
#         geo_data['serviceURL'] = remove_parameters_from_url(geo_resource.get('url'))
#         geo_data['type'] = geo_resource.get('format')
#         geo_data['name'] = remove_last_part(item.get('name'))
#         geo_data['tags'] = [tag.get('name') for tag in item.get('tags', [])]
#         geo_data['notes'] = item.get('notes')
#         geo_data['url'] = item.get('url')
#         geo_data['author'] = item.get('author')
#         geo_data['metadata_created'] = item.get('metadata_created')
#         geo_data['metadata_modified'] = item.get('metadata_modified')


#         # Add PDF and tech HTML if found
#         for resource in item.get('resources', []):
#             if resource.get('format') == "PDF":
#                 geo_data['pdf'] = resource.get('url')
#             if resource.get('format') == "HTML" and resource.get('description') == "Technische Beschreibung":
#                 geo_data['techHtml'] = resource.get('url')

#         # Add guid if exists in extras
#         for extra in item.get('extras', []):
#             if extra.get('key') == "guid":
#                 geo_data['guid'] = extra.get('value')

#         # Ensure dataset folder & write CKAN JSON
#         dataset_path = dataset_path = Path("../data/datasets") / geo_data['name']
#         dataset_path.mkdir(parents=True, exist_ok=True)

#         with open(dataset_path / "ckan.json", "w", encoding="utf-8") as f:
#             json.dump(geo_data, f, ensure_ascii=False, indent=2)

#         updated_datasets.append(geo_data['name'])

#     # Write updated dataset names to JSON
#     updated_file = "../data/datasetsUpdated.json"
#     with open(updated_file, "w", encoding="utf-8") as f:
#         json.dump(updated_datasets, f, ensure_ascii=False, indent=2)

#     print(f"✅ Datasets processed: {len(updated_datasets)}")
#     print(f"✅ Updated datasets list saved to: {updated_file}")


# parse_ckan_data()
