from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget

from Controllers.ClientSocketController import DataRequest
from Controllers.StaffViewTransaction_Controller import StaffViewTransaction
from Views.Staff_Transactions import Ui_Staff_Transactions as StaffTransactionUI

class StaffTransactions(QWidget):
    def __init__(self, transactions_ui):
        super().__init__()
        self.ui = StaffTransactionUI()
        self.transactions_ui = transactions_ui
        self.ui.setupUi(self)

        self.load_transaction_details()


        if hasattr(self.transactions_ui, 'ViewButton'):
            self.transactions_ui.ViewButton.clicked.connect(self.view_transaction)

    def load_transaction_details(self):
        try:
            # Fetch all completed check-ups
            checkups = DataRequest.send_command("GET_ALL_CHECKUP")
            # Fetch all transactions to determine their status
            transactions = DataRequest.send_command("GET_ALL_TRANSACTION")
            transaction_dict = {tran['chck_id'].strip().lower(): tran['tran_status'] for tran in transactions}

            # Debug: Log all chck_id from transactions

            # Clear the table before populating it
            self.transactions_ui.TransactionTable.clearContents()
            self.transactions_ui.TransactionTable.setRowCount(0)

            # Populate the table
            for row, checkup in enumerate(checkups):
                chck_id = checkup['chck_id'].strip().lower()

                # Fetch patient details
                pat_id = checkup['pat_id']
                patient = DataRequest.send_command("GET_PATIENT_DETAILS", pat_id)

                if not patient:
                    continue

                # Fetch doctor details
                doc_id = checkup['doc_id']
                doctor = DataRequest.send_command("GET_DOCTOR_BY_ID",doc_id)

                if not doctor:
                    continue

                # Format patient and doctor names
                pat_full_name = f"{patient['pat_lname'].capitalize()}, {patient['pat_fname'].capitalize()}"
                doc_full_name = f"{doctor['doc_lname'].capitalize()}, {doctor['doc_fname'].capitalize()}"

                # Determine the transaction status
                tran_status = transaction_dict.get(chck_id, "Pending")

                # Insert data into the table
                self.transactions_ui.TransactionTable.insertRow(row)
                self.transactions_ui.TransactionTable.setItem(row, 0,
                                                              QtWidgets.QTableWidgetItem(str(chck_id)))  # Check-up ID
                self.transactions_ui.TransactionTable.setItem(row, 1,
                                                              QtWidgets.QTableWidgetItem(pat_full_name))  # Patient Name
                self.transactions_ui.TransactionTable.setItem(row, 2,
                                                              QtWidgets.QTableWidgetItem(doc_full_name))  # Doctor Name
                self.transactions_ui.TransactionTable.setItem(row, 3, QtWidgets.QTableWidgetItem(
                    tran_status))  # Transaction Status

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load transaction details: {e}")

        self.transactions_ui.TransactionTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.transactions_ui.TransactionTable.horizontalHeader().setVisible(True)
        self.transactions_ui.TransactionTable.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.transactions_ui.TransactionTable.verticalHeader().setVisible(False)


    def view_transaction(self):
        try:
            # Get the currently selected row
            selected_row = self.transactions_ui.TransactionTable.currentRow()
            if selected_row == -1:
                QtWidgets.QMessageBox.warning(
                    self,
                    "No Selection",
                    "Please select a transaction to view."
                )
                return

            # Retrieve the chck_id from the first column of the selected row
            chck_id_item = self.transactions_ui.TransactionTable.item(selected_row, 0)
            if not chck_id_item or not chck_id_item.text():
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to retrieve check-up ID from the selected row."
                )
                return

            chck_id = chck_id_item.text().strip()

            # Ensure chck_id is a valid string
            if not isinstance(chck_id, str) or not chck_id:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    "Invalid check-up ID retrieved from the selected row."
                )
                return

            # Open the StaffViewTransaction modal with the selected chck_id
            self.staff_transaction_view = StaffViewTransaction(chck_id=chck_id, parent=self)
            self.staff_transaction_view.show()

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {e}")



