"""Example usage of TaxCloud order management features."""

from ziptax import ZipTaxClient
from ziptax.models import (
    CartItemRefundWithTaxRequest,
    CartItemWithTax,
    CreateOrderRequest,
    Currency,
    RefundTransactionRequest,
    Tax,
    TaxCloudAddress,
    UpdateOrderRequest,
)


def main():
    """Demonstrate TaxCloud order management functionality."""
    # Initialize client with TaxCloud credentials
    client = ZipTaxClient.api_key(
        api_key="your-ziptax-api-key",
        taxcloud_connection_id="25eb9b97-5acb-492d-b720-c03e79cf715a",
        taxcloud_api_key="your-taxcloud-api-key",
    )

    # Example 1: Create an order
    print("Creating an order...")
    create_request = CreateOrderRequest(
        order_id="my-order-1",
        customer_id="customer-453",
        transaction_date="2024-01-15T09:30:00Z",
        completed_date="2024-01-15T09:30:00Z",
        origin=TaxCloudAddress(
            line1="323 Washington Ave N",
            city="Minneapolis",
            state="MN",
            zip="55401-2427",
        ),
        destination=TaxCloudAddress(
            line1="323 Washington Ave N",
            city="Minneapolis",
            state="MN",
            zip="55401-2427",
        ),
        line_items=[
            CartItemWithTax(
                index=0,
                item_id="item-1",
                price=10.8,
                quantity=1.5,
                tax=Tax(amount=1.31, rate=0.0813),
            )
        ],
        currency=Currency(currency_code="USD"),
    )

    order = client.request.CreateOrder(create_request)
    print(f"Created order: {order.order_id}")
    print(f"Tax amount: ${order.line_items[0].tax.amount}")

    # Example 2: Retrieve an order
    print("\nRetrieving the order...")
    retrieved_order = client.request.GetOrder("my-order-1")
    print(f"Retrieved order: {retrieved_order.order_id}")
    print(f"Completed date: {retrieved_order.completed_date}")

    # Example 3: Update an order's completed date
    print("\nUpdating order completed date...")
    update_request = UpdateOrderRequest(completed_date="2024-01-16T10:00:00Z")
    updated_order = client.request.UpdateOrder("my-order-1", update_request)
    print(f"Updated completed date: {updated_order.completed_date}")

    # Example 4: Create a partial refund
    print("\nCreating a partial refund...")
    refund_request = RefundTransactionRequest(
        items=[
            CartItemRefundWithTaxRequest(
                item_id="item-1",
                quantity=1.0,
            )
        ]
    )
    refunds = client.request.RefundOrder("my-order-1", refund_request)
    print(f"Created {len(refunds)} refund(s)")
    print(f"Refunded tax amount: ${refunds[0].items[0].tax.amount}")

    # Example 5: Create a full refund (without specifying items)
    print("\nCreating a full refund...")
    full_refunds = client.request.RefundOrder("my-order-2")
    print(f"Created full refund for order: my-order-2")

    # Close the client
    client.close()


if __name__ == "__main__":
    main()
