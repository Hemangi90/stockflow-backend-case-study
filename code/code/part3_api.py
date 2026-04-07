from flask import jsonify
from datetime import datetime, timedelta

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def get_low_stock_alerts(company_id):
    alerts = []

    warehouses = Warehouse.query.filter_by(company_id=company_id).all()

    for warehouse in warehouses:
        inventories = Inventory.query.filter_by(warehouse_id=warehouse.id).all()

        for inv in inventories:
            product = Product.query.get(inv.product_id)

            recent_sales = Inventory_Transactions.query.filter(
                Inventory_Transactions.product_id == product.id,
                Inventory_Transactions.type == 'sale',
                Inventory_Transactions.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count()

            if recent_sales == 0:
                continue

            threshold = getattr(product, 'low_stock_threshold', 10)

            if inv.quantity < threshold:
                product_supplier = Product_Supplier.query.filter_by(product_id=product.id).first()

                supplier_data = None
                if product_supplier:
                    supplier = Supplier.query.get(product_supplier.supplier_id)
                    supplier_data = {
                        "id": supplier.id,
                        "name": supplier.name,
                        "contact_email": supplier.contact_email
                    }

                alerts.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "sku": product.sku,
                    "warehouse_id": warehouse.id,
                    "warehouse_name": warehouse.name,
                    "current_stock": inv.quantity,
                    "threshold": threshold,
                    "days_until_stockout": 10,
                    "supplier": supplier_data
                })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    })
