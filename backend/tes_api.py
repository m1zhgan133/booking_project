from flask import Flask, request, jsonify

app = Flask(__name__)

# ------------------------------------------------------- тестовая функция
@app.route('/api/check_availability', methods=['GET'])
def check_availability():
    datetime_str = request.args.get('datetime')
    try:
        # Здесь должна быть ваша логика проверки занятости мест
        # Возвращаем mock-данные для примера
        seats = {
            i: bool(i % 2 == 0)  # Случайные true/false для каждого места
            for i in range(1, 21)
        }
        return jsonify({"seats": seats})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)