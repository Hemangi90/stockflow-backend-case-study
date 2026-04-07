from flask import request, jsonify
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json

    try:
        required_fields = ['name', 'sku', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400

        try:
            price = Decimal(str(data['price']))
        except:
            return jsonify({"error": "Invalid price format"}), 400

        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=price
        )

        db.session.add(product)
        db.session.flush()

        if 'warehouse_id' in data:
            warehouse = Warehouse.query.get(data['warehouse_id'])

            if not warehouse:
                return jsonify({"error": "Invalid warehouse_id"}), 400

            inventory = Inventory(
                product_id=product.id,
                warehouse_id=warehouse.id,
                quantity=data.get('initial_quantity', 0)
            )

            db.session.add(inventory)

        db.session.commit()

        return jsonify({
            "message": "Product created successfully",
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU must be unique"}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
