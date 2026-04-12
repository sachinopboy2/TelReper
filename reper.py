from telethon.sync import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from telethon import functions, types
from os import listdir, mkdir
from sys import argv
from re import search
from colorama import Fore
import asyncio, argparse

# --- Arguments Setup (Original Style) ---
argument_parser = argparse.ArgumentParser(description='Multi-purpose Telegram Reporter by Sachin', add_help=False)
argument_parser.add_argument('-an', '--add-number', help='Add a new account')
argument_parser.add_argument('-r', '--run', help='Number of reports per account', type=int)
argument_parser.add_argument('-t', '--target', help='Target username (without @)', type=str)
argument_parser.add_argument('-m', '--mode', help='set reason of reports', choices=['spam', 'fake', 'violence', 'child_abuse', 'porn', 'geo'])
argument_parser.add_argument('-re', '--reasons', help='shows list of reasons', action='store_true')
argument_parser.add_argument('-h', '--help', action='store_true')
command_line_args = argument_parser.parse_args()

try:
    mkdir('sessions')
except: pass

session_files = [f for f in listdir('sessions') if f.endswith('.session')]
session_files.sort()
api_id = 20106942
api_hash = '3bfe2013e4399af96d78640db6dcd601'

def get_reason(mode):
    reasons = {
        'spam': types.InputReportReasonSpam(),
        'fake': types.InputReportReasonFake(),
        'violence': types.InputReportReasonViolence(),
        'child_abuse': types.InputReportReasonChildAbuse(),
        'porn': types.InputReportReasonPornography(),
        'geo': types.InputReportReasonGeoIrrelevant()
    }
    return reasons.get(mode, types.InputReportReasonSpam())

# --- Help & Reasons UI ---
if command_line_args.help:
    print(f'''Help:
  -an {Fore.LIGHTBLUE_EX}NUMBER{Fore.RESET} ~> {Fore.YELLOW}Add account{Fore.RESET}
  -r {Fore.LIGHTBLUE_EX}COUNT{Fore.RESET} -t {Fore.LIGHTBLUE_EX}TARGET{Fore.RESET} -m {Fore.LIGHTBLUE_EX}MODE{Fore.RESET} ~> {Fore.YELLOW}Run reports{Fore.RESET}
  Example: python3 {argv[0]} -r 50 -t BadChannel -m spam''')

elif command_line_args.reasons:
    print(f"List of reasons: {Fore.YELLOW}spam, fake, violence, child_abuse, pornography, geo{Fore.RESET}")

# --- Add New Account Logic ---
elif command_line_args.add_number:
    phone = command_line_args.add_number
    new_idx = len(session_files) + 1
    client = TelegramClient(f'sessions/Ac{new_idx}', api_id, api_hash)
    try:
        client.start(phone)
        print(f' [{Fore.GREEN}✅{Fore.RESET}] Account Ac{new_idx} added successfully!')
    except Exception as e:
        print(f' [{Fore.RED}!{Fore.RESET}] Error: {e}')

# --- Main Reporting Logic ---
elif command_line_args.run and command_line_args.target and command_line_args.mode:
    async def report_channel(session_file):
        s_name = session_file.replace(".session", "")
        client = TelegramClient(f'sessions/{s_name}', api_id, api_hash)
        async with client:
            try:
                me = await client.get_me()
                target = await client.get_entity(command_line_args.target)
                
                # 1. BOT CHECK: Agar bot hai toh pehle /start karna padega messages ke liye
                if isinstance(target, types.User) and target.bot:
                    await client(SendMessageRequest(peer=target, message='/start'))
                    await asyncio.sleep(2)

                # 2. JOIN CHECK: Agar channel/group hai toh join karna zaroori hai
                if isinstance(target, (types.Channel, types.Chat)):
                    try:
                        await client(JoinChannelRequest(target))
                        await asyncio.sleep(1)
                    except: pass

                # 3. MESSAGE FETCH: Reporting ke liye message IDs pick karna
                messages = await client.get_messages(target, limit=5)
                msg_ids = [m.id for m in messages] if messages else [0]
                
                report_reason = get_reason(command_line_args.mode)

                # 4. REPORT LOOP
                for i in range(command_line_args.run):
                    try:
                        # 2026 MTProto v1.40+ compatible call
                        await client(functions.messages.ReportRequest(
                            peer=target,
                            id=msg_ids,
                            option=b'', 
                            message=f"Reporting for {command_line_args.mode} content"
                        ))
                        print(f" [{Fore.GREEN}✅{Fore.RESET}] {Fore.CYAN}{me.first_name}{Fore.RESET} -> Reported {i+1}")
                        
                        # Anti-Flood Delay: ID bachane ke liye zaroori hai
                        await asyncio.sleep(3) 
                    except Exception as e:
                        print(f" [{Fore.RED}!{Fore.RESET}] Account {me.first_name} error: {e}")
                        break
            except Exception as e:
                print(f" [{Fore.RED}!{Fore.RESET}] Session {session_file} failed: {e}")

    async def run_all_accounts():
        tasks = [report_channel(s) for s in session_files]
        await asyncio.gather(*tasks)

    if not session_files:
        print(f" [{Fore.RED}!{Fore.RESET}] No accounts in 'sessions/' folder. Use -an first.")
    else:
        asyncio.run(run_all_accounts())

else:
    print(f"{Fore.MAGENTA}Sachin Reporter Tool{Fore.RESET} - use --help for info.")
