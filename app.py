from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS
import base64
import os

app = Flask(__name__)
app.config.from_pyfile('config.py')
CORS(app)

db = SQLAlchemy(app)
mail = Mail(app)

class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.LargeBinary, nullable=True)

@app.route('/dishes', methods=['GET'])
def get_dishes():
    dishes = Dish.query.all()
    result = [{"id": d.id, "name": d.name, "image": base64.b64encode(d.image).decode() if d.image else None} for d in dishes]
    return jsonify(result)

@app.route('/add_dish', methods=['POST'])
def add_dish():
    data = request.json
    image_binary = base64.b64decode(data['image']) if data.get('image') else None
    new_dish = Dish(name=data['name'], image=image_binary)
    db.session.add(new_dish)
    db.session.commit()
    return jsonify({"message": "菜品添加成功"}), 201

@app.route('/delete_dish/<int:dish_id>', methods=['DELETE'])
def delete_dish(dish_id):
    dish = Dish.query.get(dish_id)
    if not dish:
        return jsonify({"message": "菜品不存在"}), 404
    db.session.delete(dish)
    db.session.commit()
    return jsonify({"message": "菜品删除成功"}), 200

@app.route('/order', methods=['POST'])
def submit_order():
    data = request.json
    dish_names = ", ".join(data['dishes'])
    msg = Message("情侣点菜单", sender=app.config['MAIL_USERNAME'], recipients=[app.config['TARGET_EMAIL']])
    msg.body = f"您已点的菜品：{dish_names}"
    try:
        mail.send(msg)
    except Exception as e:
        return jsonify({"message": "邮件发送失败", "error": str(e)}), 500
    return jsonify({"message": "订单已提交"}), 200

if __name__ == '__main__':
    if not os.path.exists('menu.db'):
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
