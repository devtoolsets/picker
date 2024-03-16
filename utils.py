from colorama import Fore


class colorPrint:
    @staticmethod
    def focus(data: str):
        print(Fore.YELLOW + data + Fore.RESET)

    @staticmethod
    def success(data: str):
        print(Fore.LIGHTGREEN_EX + data + Fore.RESET)

    @staticmethod
    def failed(data: str):
        print(Fore.LIGHTRED_EX + data + Fore.RESET)

