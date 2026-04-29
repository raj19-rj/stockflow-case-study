"""
Part 3: Low Stock Alert API
============================
GET /api/companies/{company_id}/alerts/low-stock

Assumptions:
- Recent sales = last 30 days
- Threshold stored per product
- Days until stockout = stock / avg daily sales
- No supplier returns null in response
"""

from flask import jsonify
from datetime import datetime, timedelta
from sqlalchemy import func

@app.route('/api/companies/<int:company_id>/alerts/low-stock', 
           methods=['GET'])
def low_stock_alerts(company_id):

    # Verify company exists
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": "Company not found"}), 404

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Subquery: products with recent sales activity
    recent_sales = db.session.query(
        Sales.product_id,
        Sales.warehouse_id,
        func.sum(Sales.quantity_sold).label('total_sold')
    ).filter(
        Sales.sold_at >= thirty_days_ago
    ).group_by(
        Sales.product_id,
        Sales.warehouse_id
    ).subquery()

    # Main query: low stock products with recent sales
    results = db.session.query(
        Product,
        Warehouse,
        Inventory,
        Supplier,
        recent_sales.c.total_sold
    ).join(
        Inventory, (Inventory.product_id == Product.id)
    ).join(
        Warehouse, (Warehouse.id == Inventory.warehouse_id)
    ).join(
        recent_sales,
        (recent_sales.c.product_id == Product.id) &
        (recent_sales.c.warehouse_id == Inventory.warehouse_id)
    ).outerjoin(
        Supplier, Supplier.id == Product.supplier_id
    ).filter(
        Warehouse.company_id == company_id,
        Inventory.quantity < Product.low_stock_threshold
    ).all()

    alerts = []
    for product, warehouse, inventory, supplier, total_sold in results:

        # Calculate days until stockout
        avg_daily_sales = total_sold / 30
        if avg_daily_sales > 0:
            days_until_stockout = int(inventory.quantity / avg_daily_sales)
        else:
            days_until_stockout = None

        alerts.append({
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "warehouse_id": warehouse.id,
            "warehouse_name": warehouse.name,
            "current_stock": inventory.quantity,
            "threshold": product.low_stock_threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": {
                "id": supplier.id,
                "name": supplier.name,
                "contact_email": supplier.contact_email
            } if supplier else None
        })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    }), 200
