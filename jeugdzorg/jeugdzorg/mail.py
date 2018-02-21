import requests

def send_simple_message():
    return requests.post(
        "https://api.mailgun.net/v3/sandbox3b67b70120ad4f16b26ced71608f67ff.mailgun.org/messages",
        auth=("api", "key-a423595d8af532da36919c517b9549ff"),
        data={"from": "Mailgun Sandbox <postmaster@sandbox3b67b70120ad4f16b26ced71608f67ff.mailgun.org>",
              "to": "Maurice Guikema <maurice@mgui.nl>",
              "subject": "Hello Maurice Guikema",
              "text": "Congratulations Maurice Guikema, you just sent an email with Mailgun!  You are truly awesome!"})