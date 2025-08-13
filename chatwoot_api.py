# chatwoot_api.py
import requests
import json
from config import config

def get_headers():
    return {"api_access_token": config.CHATWOOT_API_TOKEN, "Content-Type": "application/json; charset=utf-8"}

def get_multipart_headers():
    return {"api_access_token": config.CHATWOOT_API_TOKEN}

def get_base_url():
    return f"{config.CHATWOOT_URL}/api/v1/accounts/{config.CHATWOOT_ACCOUNT_ID}"

def create_api_inbox(name, webhook_url):
    url = f"{get_base_url()}/inboxes"
    payload = {"name": name, "channel": {"type": "api", "webhook_url": webhook_url}}
    response = requests.post(url, headers=get_headers(), json=payload)
    response.raise_for_status()
    return response.json()

def create_webhook(webhook_url):
    url = f"{get_base_url()}/webhooks"
    payload = {"webhook": {"url": webhook_url, "subscriptions": ["message_created"]}}
    response = requests.post(url, headers=get_headers(), json=payload)
    response.raise_for_status()
    return response.json()

def find_or_create_contact(identifier, name, email=None):
    search_url = f"{get_base_url()}/contacts/search"
    response = requests.get(search_url, headers=get_headers(), params={'q': str(identifier)})
    response.raise_for_status()
    data = response.json()
    if data['meta']['count'] > 0:
        return data['payload'][0]
    else:
        create_url = f"{get_base_url()}/contacts"
        payload = {"name": name, "email": email, "identifier": str(identifier)}
        response = requests.post(create_url, headers=get_headers(), data=json.dumps(payload))
        response.raise_for_status()
        return response.json()['payload']['contact']

def create_conversation(inbox_id, contact_id, message_body, custom_attributes=None):
    conv_url = f"{get_base_url()}/conversations"
    payload = {"inbox_id": inbox_id, "contact_id": contact_id, "message": {"content": message_body, "message_type": "incoming"}, "status": "open"}
    if custom_attributes:
        payload["custom_attributes"] = custom_attributes
    response = requests.post(conv_url, headers=get_headers(), data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
    response.raise_for_status()
    return response.json()

def create_conversation_with_attachment(inbox_id, contact_id, message_body, custom_attributes, file_content, filename):
    conv_url = f"{get_base_url()}/conversations"
    data = {"inbox_id": inbox_id, "contact_id": contact_id, "content": message_body, "message_type": "incoming", "status": "open", "custom_attributes": json.dumps(custom_attributes)}
    files = {'attachments[]': (filename, file_content)}
    response = requests.post(conv_url, headers=get_multipart_headers(), data=data, files=files, timeout=45)
    response.raise_for_status()
    return response.json()

def search_conversation(pack_id):
    filter_url = f"{get_base_url()}/conversations/filter"
    payload = {"payload": [{"attribute_key": "meli_pack_id", "attribute_model": "conversation_attribute", "filter_operator": "equal_to", "values": [str(pack_id)], "query_operator": "and"}]}
    response = requests.post(filter_url, headers=get_headers(), json=payload)
    response.raise_for_status()
    data = response.json()
    return data['payload'][0] if data['meta']['count'] > 0 else None

def add_message_to_conversation(conversation_id, message_body, file_content=None, filename=None):
    message_url = f"{get_base_url()}/conversations/{conversation_id}/messages"
    if file_content:
        data = {"content": message_body, "message_type": "incoming"}
        files = {'attachments[]': (filename, file_content)}
        response = requests.post(message_url, headers=get_multipart_headers(), data=data, files=files, timeout=45)
    else:
        payload = {"content": message_body, "message_type": "incoming"}
        response = requests.post(message_url, headers=get_headers(), json=payload)
    response.raise_for_status()
    return response.json()
