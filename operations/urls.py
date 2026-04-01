from django.urls import path
from .views import (
    product_list_create_view,
    product_update_view,
    product_delete_view,
    restock_product_view,
    order_list_create_view,
    update_order_status_view,
    operations_dashboard_view,
    low_stock_alerts_view,
    import_sales_lead_to_order_view,
)

urlpatterns = [
    path("dashboard/", operations_dashboard_view, name="operations_dashboard"),
    path("products/", product_list_create_view, name="product_list_create"),
    path("products/<str:sku>/", product_update_view, name="product_update"),
    path("products/<str:sku>/delete/", product_delete_view, name="product_delete"),
    path("products/<str:sku>/restock/", restock_product_view, name="product_restock"),
    path("orders/", order_list_create_view, name="order_list_create"),
    path("orders/<int:order_id>/status/", update_order_status_view, name="order_status_update"),
    path("alerts/", low_stock_alerts_view, name="low_stock_alerts"),
    path("import-sales-lead/<int:lead_id>/", import_sales_lead_to_order_view, name="import_sales_lead"),
]