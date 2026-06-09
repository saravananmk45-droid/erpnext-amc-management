import frappe
from frappe.utils import add_days, today


def check_expiring_contracts():
    contracts = frappe.get_all(
        "AMC Contract",
        filters={
            "end_date": ["between", [today(), add_days(today(), 30)]]
        },
        fields=[
            "name",
            "customer",
            "end_date"
        ]
    )

    for contract in contracts:

        customer_email = frappe.db.get_value(
            "Customer Email",
            {"customer": contract.customer},
            "email"
        )

        if customer_email:

            frappe.sendmail(
                recipients=[customer_email],
                subject="AMC Contract Expiry Reminder",
                message=f"""
Dear Customer,

Your AMC Contract is nearing expiry.

Contract: {contract.name}
Customer: {contract.customer}
Expiry Date: {contract.end_date}

Please contact us for renewal.

Regards,
AMC Management Team
"""
            )
