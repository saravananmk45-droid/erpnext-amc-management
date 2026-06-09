# Copyright (c) 2026, Saravanan M K and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate


class AMCVisit(Document):

    def validate(self):

        # Validation 1: AMC Contract mandatory
        if not self.amc_contract:
            frappe.throw("AMC Contract is mandatory")

        # Get AMC Contract document
        amc_contract = frappe.get_doc(
            "AMC Contract",
            self.amc_contract
        )

        # Validation 2: Free Visits Available
        if amc_contract.remaining_visits <= 0:
            frappe.throw(
                "No Free Visits Remaining in this AMC Contract"
            )

        amc_start = getdate(amc_contract.start_date)
        amc_end = getdate(amc_contract.end_date)
        visit_date = getdate(self.visit_date)

        # Validation 3: Visit Date cannot be before AMC Start Date
        if visit_date < amc_start:
            frappe.throw(
                "Visit Date cannot be before AMC Contract Start Date"
            )

        # Validation 4: Visit Date cannot be after AMC End Date
        if visit_date > amc_end:
            frappe.throw(
                "Visit Date cannot be after AMC Contract End Date"
            )

        # Validation 5: Remarks minimum 10 characters
        if self.remarks and len(self.remarks.strip()) < 10:
            frappe.throw(
                "Remarks must contain at least 10 characters"
            )

        # Validation 6: Visit Outcome mandatory when Completed
        if self.status == "Completed" and not self.visit_outcome:
            frappe.throw(
                "Visit Outcome is mandatory when Status is Completed"
            )

        # Validation 7: Engineer mandatory
        if not self.engineer:
            frappe.throw(
                "Engineer is mandatory"
            )

    def after_insert(self):

        amc_contract = frappe.get_doc(
            "AMC Contract",
            self.amc_contract
        )
        customer_email = frappe.db.get_value(
            "Customer Email",
            {"customer": amc_contract.customer},
            "email"
        )

        used_visits = (
            amc_contract.used_free_visits or 0
        ) + 1

        remaining_visits = (
            amc_contract.number_of_free_visits or 0
        ) - used_visits

        amc_contract.used_free_visits = used_visits
        amc_contract.remaining_visits = remaining_visits

        amc_contract.save(
            ignore_permissions=True
        )

        # Email Notification
        if customer_email:
            frappe.sendmail(
                recipients=[customer_email],
                subject="AMC Visit Created Successfully",
                message=f"""
                AMC Visit has been created.

                AMC Contract: {self.amc_contract}
                Visit Date: {self.visit_date}
                Engineer: {self.engineer}
                Status: {self.status}

                Remaining Visits: {remaining_visits}
                """
            )
