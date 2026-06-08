import frappe
from frappe.model.document import Document
from frappe.utils import getdate, nowdate


class AMCContract(Document):

    def validate(self):

        start_date = getdate(self.start_date)
        end_date = getdate(self.end_date)

        # Validation 1: Contract Value must be greater than 0
        if self.contract_value <= 0:
            frappe.throw("Contract Value must be greater than 0")

        # Validation 2: End Date must be after Start Date
        if end_date <= start_date:
            frappe.throw("End Date must be greater than Start Date")

        # Validation 3: Free Visits must be at least 1
        if self.number_of_free_visits < 1:
            frappe.throw("Number of Free Visits must be at least 1")

        # Validation 4: AMC duration must be at least 30 days
        if (end_date - start_date).days < 30:
            frappe.throw("AMC Contract must be at least 30 days")

        # Validation 5: Free Visits should not exceed 12
        if self.number_of_free_visits > 12:
            frappe.throw("Number of Free Visits cannot exceed 12")

        # Validation 6: End Date should not be in the past
        if end_date < getdate(nowdate()):
            frappe.throw("End Date cannot be in the past")

        # Validation 7: Prevent duplicate active AMC contracts
        existing_contract = frappe.db.exists(
            "AMC Contract",
            {
                "customer": self.customer,
                "status": ["!=", "Cancelled"],
                "name": ["!=", self.name]
            }
        )

        if existing_contract:
            frappe.throw(
                f"An active AMC Contract already exists for customer {self.customer}"
            )
