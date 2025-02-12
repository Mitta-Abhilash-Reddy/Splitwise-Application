import csv
from datetime import datetime

class User:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone
        self.balance = 0  
        self.transactions = []  

    def add_transaction(self, payer, participants, amount, description):
        transaction_detail = f"{payer} paid {amount:.2f} for {', '.join(participants)} - {description}"
        self.transactions.append(transaction_detail)

    def details(self):
        print(f"Name: {self.name}, Phone: {self.phone}, Balance: {self.balance:.2f}")
        print("Transaction History:")
        for transaction in self.transactions:
            print("  -", transaction)


class Node:
    def __init__(self, user):
        self.user = user
        self.next = None


class UserLinkedList:
    def __init__(self):
        self.head = None

    def add_user(self, user):
        new_node = Node(user)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def find_user(self, name):
        current = self.head
        while current:
            if current.user.name == name:
                return current.user
            current = current.next
        return None

    def display_users(self):
        current = self.head
        print(f"{'Name':<15} {'Phone':<15}")
        print("-" * 30) 
        while current:
            print(f"{current.user.name:<15} {current.user.phone:<15}")
            current = current.next
        print("-" * 30)  


class TransactionQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, transaction):
        self.queue.append(transaction)

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def is_empty(self):
        return len(self.queue) == 0


class Group:
    def __init__(self):
        self.users = UserLinkedList()
        self.transactions = TransactionQueue()

    def add_user(self, user_name=None, user_phone=None):
        while True:
            user_name = input("Enter user name (or enter 0 to go back): ").strip()
            if user_name == '0':
                return
            user_phone = input("Enter user phone number (or enter 0 to go back): ").strip()
            if user_phone == '0':
                return

            if self.users.find_user(user_name) is None:
                user = User(user_name, user_phone)
                self.users.add_user(user)
                print(f"User {user_name} added to the group.")
            else:
                print(f"{user_name} is already in the group.")

    def add_expense(self, payer, amount, description=""):
        payer_user = self.users.find_user(payer)
        if not payer_user:
            print("Payer not found in the group.")
            return

        participants = []
        print(" Available users ")
        self.users.display_users()
        pay_for_all = input("Do you want to pay for all participants? (y/n): ").strip().lower()
        
        if pay_for_all == 'y':
            current = self.users.head
            while current:
                participants.append(current.user.name)
                current = current.next
        else:
            participant_names = input("Enter participant names (comma-separated): ").split(',')
            for name in participant_names:
                participant = self.users.find_user(name.strip())
                if participant:
                    participants.append(participant.name)
                else:
                    print(f"{name} not found in the group.")
        
        split_type = input("Split type (equal/shares/percentage): ").strip().lower()
        shares = None
        if split_type in ['shares', 'percentage']:
            shares = [float(s) for s in input("Enter shares or percentages (comma-separated): ").split(',')]
        
        share_distribution = self.calculate_split(amount, participants, split_type, shares)
        
        payer_user.balance -= sum(share_distribution.values())
        payer_user.add_transaction(payer, participants, amount, description)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.enqueue((timestamp, payer, participants, amount, description))

        for participant, owed_amount in share_distribution.items():
            if participant != payer:
                participant_user = self.users.find_user(participant)
                participant_user.balance += owed_amount
                participant_user.add_transaction(payer, [participant], owed_amount, description)

    def calculate_split(self, amount, participants, split_type, shares=None):
        if split_type == "equal":
            split_amount = amount / len(participants)
            return {p: split_amount for p in participants}
        elif split_type == "shares" and shares:
            total_shares = sum(shares)
            return {p: (s / total_shares) * amount for p, s in zip(participants, shares)}
        elif split_type == "percentage" and shares:
            if sum(shares) != 100:
                print("Percentage values do not add up to 100.")
                return {}
            return {p: (s / 100) * amount for p, s in zip(participants, shares)}
        else:
            print("Invalid split type or shares input.")
            return {}

    def show_balances(self):
        print("\n--- Current Balances ---")
        current = self.users.head
        while current:
            user = current.user
            if user.balance > 0:
                print(f"{user.name} should receive money: {user.balance:.2f}")
            elif user.balance < 0:
                print(f"{user.name} should pay money: {abs(user.balance):.2f}")
            else:
                print(f"{user.name} has a balanced account.")
            current = current.next
        print("For more clarification, select 'Settle Up'.")

    def pay(self, payer_name, payee_name, amount):
        payer = self.users.find_user(payer_name)
        payee = self.users.find_user(payee_name)

        if not payer or not payee:
            print("Either payer or payee does not exist in the group.")
            return

        if abs(payer.balance) >= amount or payer.balance >= 0:
            payer.balance += amount  
            payee.balance -= amount  
            payer.add_transaction(payer_name, [payee_name], amount, "Direct payment")
            payee.add_transaction(payer_name, [payee_name], amount, "Received payment")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.transactions.enqueue((timestamp, payer_name, [payee_name], amount, "Direct payment"))
            
            print(f"{payer_name} paid {payee_name} an amount of {amount:.2f}")
        else:
            print(f"{payer_name} does not have enough debt capacity to pay {payee_name}")

    def export_transactions(self):
        with open("transactions.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "Payer", "Paid for", "Amount", "Description"])
            for transaction in self.transactions.queue:
                writer.writerow(transaction)
        print("Transactions exported to transactions.csv.")

    def settle_up(self):
        creditors, debtors = [], []
        current = self.users.head
        while current:
            if current.user.balance > 0:
                creditors.append((current.user.name, current.user.balance))
            elif current.user.balance < 0:
                debtors.append((current.user.name, -current.user.balance))  
            current = current.next

        print("\n--- Settle Up ---")
        
        
        while creditors and debtors:
            creditor, credit_amount = creditors.pop(0)
            debtor, debt_amount = debtors.pop(0)
            
            
            amount_to_settle = min(credit_amount, debt_amount)
            print(f"{debtor} should pay {creditor} an amount of {amount_to_settle:.2f}")

            
            credit_amount -= amount_to_settle
            debt_amount -= amount_to_settle

            
            if credit_amount > 0:
                creditors.append((creditor, credit_amount))  
            if debt_amount > 0:
                debtors.append((debtor, debt_amount))  

    def display_menu(self):
        while True:
            print("\n--- Menu ---")
            print("1. Add User")
            print("2. Add Expense")
            print("3. Show Balances")
            print("4. Settle Up")
            print("5. Show User Details")
            print("6. Export Transactions to CSV")
            print("7. Pay Individual")
            print("8. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                self.add_user()
            elif choice == '2':
                payer = input("Enter payer's name: ").strip()
                amount = float(input("Enter amount: "))
                description = input("Enter a description for the expense: ")
                self.add_expense(payer, amount, description)
            elif choice == '3':
                self.show_balances()
            elif choice == '4':
                self.settle_up()
            elif choice == '5':
                user_name = input("Enter user name to search: ").strip()
                user = self.users.find_user(user_name)
                if user:
                    user.details()
                else:
                    print(f"User {user_name} not found.")
            elif choice == '6':
                self.export_transactions()
            elif choice == '7':
                payer_name = input("Enter payer's name: ").strip()
                payee_name = input("Enter payee's name: ").strip()
                amount = float(input("Enter amount to pay: "))
                self.pay(payer_name, payee_name, amount)
            elif choice == '8':
                print("Exiting...")
                break
            else:
                print("Invalid option.")


# Initialize and start the application
group = Group()
print("welcome to SPLIT-EXPENSE")
print("group has been created")
group.display_menu()

