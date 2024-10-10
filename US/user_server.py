# Luwei Wang
# lw3511

from flask import Flask, request, jsonify
import requests
import socket

app = Flask(__name__)

def dns_query(as_ip, as_port, hostname):
    query = f"TYPE=A\nNAME={hostname}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(query.encode(), (as_ip, int(as_port)))
    print(as_ip, as_port)
    data, _ = sock.recvfrom(1024) 
    response = data.decode()
    if "Failure" in response:
        print(response)
    else:
        print(f"Response: {response}")
        dns_message_lines = response.strip().split('\n')
        dns_message_dict = {line.split('=')[0]: line.split('=')[1] for line in dns_message_lines}
        target_ip = dns_message_dict.get("VALUE")
        return target_ip

@app.route('/fibonacci', methods=['GET'])
def get_fibonacci():
    param = {key: request.args.get(key) for key in ["hostname", "fs_port", "number", "as_ip", "as_port"]}
    missing = [key for key in param if not param[key]]
    if missing:
        return f"Bad Request: Missing parameter(s) [{", ".join(missing)}]", 400

    try:
        target_ip = dns_query(param['as_ip'], param['as_port'], param['hostname'])

        fs_url = f"http://{target_ip}:{param["fs_port"]}/fibonacci?number={param["number"]}"
        fs_response = requests.get(fs_url)

        if fs_response.status_code == 200:
            return jsonify({'result': fs_response.json()}), 200
        else:
            return jsonify({'error': 'Request Failed'}), fs_response.status_code

    except requests.RequestException as e:
        return f"Error: {str(e)}", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


# /fibonacci?hostname=fibonacci.com&fs_port=K&number=X&as_ip=Y&as_port=Z