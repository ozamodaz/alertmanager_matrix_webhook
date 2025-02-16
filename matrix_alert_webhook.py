#!/usr/bin/env python3
import os
import uuid
import json
import requests

from flask import Flask, request
from jinja2 import Template
import markdown2  # pip install markdown2

HOMESERVER = os.environ.get("HOMESERVER", "https://your.matrix.server")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
ROOM_ID = os.environ.get("ROOM_ID", "!yourroomid:your.matrix.server")
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "5001"))
TEMPLATE_PATH = os.environ.get("TEMPLATE_PATH", None)

app = Flask(__name__)

def load_template():
    default_template = """{% if labels.severity == "critical" %}🔴 {% elif labels.severity == "warning" %}🟡 {% else %}⚪ {% endif %}**{{ summary }}**

{{ description|replace("\\n","  \\n") }}

<ul style="margin:0; padding-left: 1em;">
{% for key, value in labels.items() if key not in ["alertname", "severity"] %}
  <li style="margin:0; padding:0;"><strong>{{ key }}</strong>: {{ value }}</li>
{% endfor %}
</ul>
"""
    if TEMPLATE_PATH:
        try:
            with open(TEMPLATE_PATH, "r") as f:
                return Template(f.read())
        except Exception as e:
            print(f"Error loading template from {TEMPLATE_PATH}: {e}")
    return Template(default_template)

template = load_template()

def send_matrix_message(markdown_message):
    """
    Convert the Markdown message to HTML and send both as 'org.matrix.custom.html'.
    """
    # No 'nl2br' since we're manually forcing line breaks with "  \n"
    html_message = markdown2.markdown(markdown_message)

    txn_id = str(uuid.uuid4())
    url = f"{HOMESERVER}/_matrix/client/r0/rooms/{ROOM_ID}/send/m.room.message/{txn_id}?access_token={ACCESS_TOKEN}"

    payload = {
        "msgtype": "m.text",
        "format": "org.matrix.custom.html",
        "body": markdown_message,      # Plain-text fallback
        "formatted_body": html_message # HTML version
    }

    headers = {"Content-Type": "application/json"}
    response = requests.put(url, headers=headers, data=json.dumps(payload))
    return response

@app.route("/", methods=["POST"])
def alertmanager_webhook():
    data = request.get_json()

    # Extract annotations (summary, description)
    annotations = data.get("commonAnnotations")
    if not annotations and data.get("alerts"):
        annotations = data["alerts"][0].get("annotations", {})
    summary = annotations.get("summary", "No summary provided")
    description = annotations.get("description", "No description provided")

    # Extract labels
    labels = data.get("commonLabels")
    if not labels and data.get("alerts"):
        labels = data["alerts"][0].get("labels", {})

    # Render the message with Jinja (forcing line breaks in the template)
    rendered_md = template.render(summary=summary, description=description, labels=labels)

    resp = send_matrix_message(rendered_md)
    if resp.status_code == 200:
        return "Message sent to Matrix", 200
    else:
        return f"Failed to send message: {resp.text}", resp.status_code

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=LISTEN_PORT)
