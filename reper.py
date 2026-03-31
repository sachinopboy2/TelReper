from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, FloodWaitError
from telethon import functions, types
from os import listdir, mkdir, path
from sys import argv
from re import search
from colorama import Fore, init
import asyncio, argparse

# Colorama initialize for Windows compatibility
init(autoreset=True)

argument_parser = argparse.ArgumentParser(description='Telegram Reporting Tool', add_help=False)
argument_parser.add_argument('-an', '--add-number', help='Add a new account')
argument_parser.add_argument('-r', '--run', help='Number of reports', type=int)
argument_parser.add_argument('-t', '--target', help='Target username (without @)', type=str)
argument_parser.add_argument('-m', '--mode', help='Reason', choices=['spam', 'fake_account', 'violence', 'child_abuse', 'pornography', 'geoirrelevant'])
argument_parser.add_argument('-re', '--reasons', action='store_true')
argument_parser.add_argument('-h', '--help', action='store_true')
args = argument_parser.parse_args()

if not path.exists('sessions'):
    mkdir('sessions')

api_id = 25148883
api_hash = 'abc30c3b47a075ec9a0854b3015ef210'

# --- Reporting Logic ---
async def report_channel(session_path, target, count, mode):
    client = TelegramClient(session_path, api_id, api_hash)
    try:
        await client.start()
        me = await client.get_me()
        print(f" [{Fore.CYAN}i{Fore.RESET}] Account {Fore.YELLOW}{me.first_name}{Fore.RESET} logic started...")

        try:
            entity = await client.get_entity(target)
            messages = await client.get_messages(entity, limit=5)
            msg_ids = [m.id for m in messages]
        except Exception as e:
            print(f" [{Fore.RED}!{Fore.RESET}] Target error: {e}")
            return

        # Reason Mapping
        reasons = {
            'spam': types.InputReportReasonSpam(),
            'fake_account': types.InputReportReasonFake(),
            'violence': types.InputReportReasonViolence(),
            'child_abuse': types.InputReportReasonChildAbuse(),
            'pornography': types.InputReportReasonPornography(),
            'geoirrelevant': types.InputReportReasonGeoIrrelevant()
        }

        selected_reason = reasons.get(mode, types.InputReportReasonSpam())

        for i in range(1, count + 1):
            try:
                # Reporting the Peer
                await client(functions.account.ReportPeerRequest(
                    peer=entity,
                    reason=selected_reason,
                    message=f"Reporting for {mode}"
                ))
                print(f" [{Fore.GREEN}✅{Fore.RESET}] Reported | Ac: {Fore.YELLOW}{me.first_name}{Fore.RESET} | Count: {Fore.BLUE}{i}{Fore.RESET}")
                await asyncio.sleep(2) # Avoid immediate flood
            except FloodWaitError as e:
                print(f" [{Fore.RED}!{Fore.RESET}] Sleeping for {e.seconds}s (FloodWait)")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f" [{Fore.RED}!{Fore.RESET}] Error: {e}")
                break
    finally:
        await client.disconnect()

# --- Main Execution Flow ---
async def main():
    session_files = [f for f in listdir('sessions') if f.endswith('.session')]
    
    if args.help:
        print(f"Usage: python {argv[0]} -r 10 -t target_user -m spam")
    
    elif args.reasons:
        print("Reasons: spam, fake_account, violence, child_abuse, pornography, geoirrelevant")

    elif args.add_number:
        phone = args.add_number
        new_id = len(session_files) + 1
        client = TelegramClient(f'sessions/Ac{new_id}', api_id, api_hash)
        await client.start(phone)
        print(f" [{Fore.GREEN}✅{Fore.RESET}] Account added as Ac{new_id}")
        await client.disconnect()

    elif args.run and args.target and args.mode:
        if not session_files:
            print(f" [{Fore.RED}!{Fore.RESET}] No accounts found in /sessions folder!")
            return

        tasks = []
        for f in session_files:
            s_path = path.join('sessions', f.replace('.session', ''))
            tasks.append(report_channel(s_path, args.target, args.run, args.mode))
        
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
    
