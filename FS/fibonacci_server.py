# Luwei Wang
# lw3511

from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

@app.route('/register', methods=['PUT'])
def register():
    try:
        param = {key: request.json.get(key) for key in ["hostname", "ip", "as_ip", "as_port"]}
        missing = [key for key in param if not param[key]]
        if missing:
            return f"Bad Request: Missing parameter(s) [{", ".join(missing)}]", 400

        dns_message = f"TYPE=A\nNAME={param["hostname"]}\nVALUE={param["ip"]}\nTTL=10\n"
        print(f"Registering: \n{dns_message}")

        print(f"Sent DNS message to {param["as_ip"]}:{param["as_port"]}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(dns_message.encode(), (param["as_ip"], int(param["as_port"])))

        response, addr = sock.recvfrom(1024)
        print(response)
        if "Success" in response.decode():
            return "Registered successfully", 201
        else:
            raise

    except Exception as e:
        return f"Registration Error: {e}", 400


@app.route('/fibonacci', methods=['GET'])
def fibonacci():
    try:
        number = request.args.get('number')

        if not number or not number.isdigit():
            return "Bad Request: Invalid number format", 400
        
        n = int(number)
        result = calculate_fibonacci(n)
        return jsonify({'result': result}), 200

    except Exception as e:
        return f"Error: {str(e)}", 400


def calculate_fibonacci(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
    return b


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)
