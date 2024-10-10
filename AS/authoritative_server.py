import socket
import json

UDP_IP = "0.0.0.0"
UDP_PORT = 53533
DNS_RECORD_FILENAME = "dns_records.json"

def save_dns_records(dns_records):
    with open(DNS_RECORD_FILENAME, 'w') as f:
        json.dump(dns_records, f)

def load_dns_records():
    try:
        with open(DNS_RECORD_FILENAME, 'r') as f:
            dns_records = json.load(f)
    except FileNotFoundError:
        dns_records = {}
    return dns_records

def handle_registration(dns_records, data):
    lines = data.strip().split('\n')
    param = {key: value for key, value in [line.split('=') for line in lines]}
    print(f"Registing record: {param}")

    if all([param.get(key) for key in ["TYPE", "NAME", "VALUE", "TTL"]]) and param.get("TYPE") == "A":
        dns_records[param["NAME"]] = {"VALUE": param["VALUE"], "TTL": param["TTL"]}
        save_dns_records(dns_records)
        return "DNS Registration Success"
    else:
        return "DNS Registration Failure"

def handle_query(dns_records, data):
    lines = data.strip().split('\n')
    param = {key: value for key, value in [line.split('=') for line in lines]}
    print(f"DNS Query for: {param["NAME"]}")

    if all([param.get(key) for key in ["TYPE", "NAME"]]) and param.get("TYPE") == "A" and param.get("NAME") in dns_records.keys():
        record = dns_records[param["NAME"]]
        response = f"TYPE=A\nNAME={param["NAME"]}\nVALUE={record['VALUE']}\nTTL={record['TTL']}\n"
        return response
    else:
        return "DNS Query Failure: No matching record found"

def start_server():
    dns_records = load_dns_records()
    print(f"Current DNS Records:\n{dns_records}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Authoritative Server (AS) listening on port {UDP_PORT}")

    while True:
        data, addr = sock.recvfrom(512)
        data = data.decode()
        print(f"Received message: {data} from {addr}")

        if "VALUE" in data:
            response = handle_registration(dns_records, data)
        else:
            response = handle_query(dns_records, data)

        sock.sendto(response.encode(), addr)
        print(f"Sent response to {addr}: {response}")

if __name__ == "__main__":
    start_server()
