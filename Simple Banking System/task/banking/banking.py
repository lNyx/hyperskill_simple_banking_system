from enum import Enum, unique
import random
from .cc_db import CreditCardsDB


# randomly generates a 9-digit account number.
# The card is: 400000 + account number + checksum number.


CARD_NUMBER_LENGTH = 16


@unique
class MainMenuItems(Enum):
    CREATE = '1'
    LOGIN = '2'
    EXIT = '0'

    def __str__(self):
        return {MainMenuItems.CREATE: "Create an account",
                MainMenuItems.LOGIN: "Log into account",
                MainMenuItems.EXIT: "Exit"}.get(self)


@unique
class UserMenuItems(Enum):
    BALANCE = '1'
    DEPOSIT = '2'
    TRANSFER = '3'
    CLOSE_ACCOUNT = '4'
    LOGOUT = '5'
    EXIT = '0'

    def __str__(self):
        return {UserMenuItems.BALANCE: "Balance",
                UserMenuItems.DEPOSIT: "Add income",
                UserMenuItems.TRANSFER: "Do transfer",
                UserMenuItems.CLOSE_ACCOUNT: "Close account",
                UserMenuItems.LOGOUT: "Log out",
                UserMenuItems.EXIT: "Exit"}.get(self)


def display_menu(enum_cls):
    for item in enum_cls:
        print(f"{item.value}. {str(item)}")


def make_menu_item(item, enum_cls):
    return enum_cls(item) if item in [m.value for m in enum_cls] else None


def is_valid_money_amount(amount: str):
    """a positive number
    """
    return amount.isnumeric() and int(amount) > 0


class CreditCard:
    __bin = "400000"

    def __init__(self, cc_num=None, cc_pin=None):
        self.number = cc_num or CreditCard.__generate_new_card_number()
        self.pin = cc_pin or CreditCard.__generate_new_pin()

    @staticmethod
    def __luhn(card_number_no_checksum):
        res = [2 * int(c) if (i + 1) % 2 else int(c) for i, c in enumerate(card_number_no_checksum)]
        res = [i - 9 if i > 9 else i for i in res]
        mid_sum = sum(res)
        return str((10 - mid_sum % 10) % 10)

    @staticmethod
    def __generate_new_card_number():
        random.seed()
        new_card_number = CreditCard.__bin + "".join([str(random.randint(0, 9)) for _ in range(9)])
        checksum = CreditCard.__luhn(new_card_number)
        new_card_number += checksum

        return new_card_number

    @staticmethod
    def __generate_new_pin():
        random.seed()
        return str(random.randint(0, 9999)).zfill(4)

    @staticmethod
    def is_valid_card_number(card_number):
        return card_number.isnumeric() and len(card_number) == CARD_NUMBER_LENGTH \
               and card_number[-1] == CreditCard.__luhn(card_number[:-1])


def main():
    with CreditCardsDB() as db:

        while not db.create_card_table():
            pass

        while True:

            display_menu(MainMenuItems)
            action = make_menu_item(input(), MainMenuItems)

            if action is MainMenuItems.CREATE:
                new_cc = CreditCard()

                while db.card_exists(new_cc.number):
                    new_cc = CreditCard()

                if db.add_new_card(new_cc.number, new_cc.pin):
                    print(f"\nYour card has been created\n"
                          f"Your card number:\n{new_cc.number}\n"
                          f"Your card PIN:\n{new_cc.pin}\n")

                else:
                    print("Please try again..")

            elif action is MainMenuItems.LOGIN:
                card = CreditCard(input("\nEnter your card number:\n"), input("Enter your PIN:\n"))

                if db.verify_card(card.number, card.pin):
                    print("\nYou have successfully logged in!\n")

                    while True:

                        display_menu(UserMenuItems)
                        action = make_menu_item(input(), UserMenuItems)

                        if action is UserMenuItems.BALANCE:
                            print(f"\nBalance: {db.get_card_balance(card.number, card.pin)}\n")

                        elif action is UserMenuItems.DEPOSIT:
                            amount = input("\nEnter income:\n")

                            if not is_valid_money_amount(amount):
                                print("\nWrong input..\n")
                                continue

                            if db.deposit_to_card(card.number, int(amount)):
                                print("\nIncome was added!\n")

                            else:
                                print("\nPlease try again..")

                        elif action is UserMenuItems.TRANSFER:
                            to_card_number = input("\nTransfer\nEnter card number:\n")

                            if not CreditCard.is_valid_card_number(to_card_number):
                                print("Probably you made a mistake in the card number. Please try again!\n")
                                continue

                            elif not db.card_exists(to_card_number):
                                print("Such a card does not exist.\n")
                                continue

                            funds_to_transfer = input("Enter how much money you want to transfer:\n")

                            if not is_valid_money_amount(funds_to_transfer):
                                print("Please enter a positive number.\n")
                                continue

                            elif db.get_card_balance(card.number, card.pin) < int(funds_to_transfer):
                                print("Not enough money!\n")
                                continue

                            if db.transfer_funds(card.number, card.pin, to_card_number, int(funds_to_transfer)):
                                print("Success!\n")

                            else:
                                print("\nPlease try again..\n")

                        elif action is UserMenuItems.CLOSE_ACCOUNT:
                            if db.delete_card(card.number, card.pin):
                                print("\nThe account has been closed!\n")
                                break
                            else:
                                print("\nPlease try again..\n")

                        elif action is UserMenuItems.LOGOUT:
                            print("\nYou have successfully logged out!\n")
                            break

                        elif action is UserMenuItems.EXIT:
                            print("\nBye!")
                            exit()

                        else:
                            print("\nWrong action..\n")

                else:
                    print("\nWrong card number or PIN!\n")

            elif action is MainMenuItems.EXIT:
                print("\nBye!")
                exit()

            else:
                print("\nWrong action..\n")


if __name__ == "__main__":
    main()
