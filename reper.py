import asyncio
import os
import argparse
import random
import re
import time
import sys
from telethon import TelegramClient, functions, types, errors
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from colorama import Fore, init, Style

# Initialize Colorama for aesthetic CLI
init(autoreset=True)

# --- ADVANCED CONFIGURATION ---
API_ID = 20106942 
API_HASH = '3bfe2013e4399af96d78640db6dcd601'
SESSION_DIR = 'sessions'

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# --- LEGAL COMPLAINT GENERATOR ---
def generate_legal_report(mode, entity_name, bio_content, links):
    link_report = f" Detected malicious links: {', '.join(links)}" if links else ""
    
    templates = {
        'child_abuse': (
            f"URGENT LEGAL NOTICE: This entity ({entity_name}) is involved in the distribution and promotion "
            "of prohibited CSAM content. This is a severe violation of international law. {link_report}"
        ),
        'violence': (
            f"CRITICAL SAFETY WARNING: The entity {entity_name} is actively inciting real-world violence and "
            f"promoting extremist ideologies. Public safety is at risk. {link_report}"
        ),
        'pornography': (
            f"POLICY VIOLATION: Non-consensual sexual content and prohibited adult media are being distributed "
            f"by this entity. Violates Telegram's searchable content regulations. {link_report}"
        ),
        'drugs': (
            f"ILLEGAL TRAFFICKING: Evidence of illegal drug sales and prohibited substance distribution "
            f"identified within this entity's activities. Bio: {bio_content[:50]}..."
        ),
        'personal_details': (
            f"PRIVACY BREACH (DOXXING): This entity is sharing sensitive personal information of individuals "
            "without legal consent. Harassment campaign detected."
        ),
        'spam': (
            f"DECEPTIVE PRACTICES: This bot/channel is using high-traffic keywords (e.g., Instagram Viral) "
            f"to lure users into a phishing network. Deceptive redirects found. {link_report}"
        ),
        'fake_account': (
            f"IMPERSONATION FRAUD: This entity is fraudulently claiming to be an official representative. "
            f"Using deceptive branding to scam users. {link_report}"
        ),
        'other': (
            f"GENERAL TOS VIOLATION: This entity {entity_name} has multiple breaches of Telegram's guidelines. "
            f"Bio Analysis: {bio_content[:100]}... {link_report}"
        )
    }
    return templates.get(mode.lower(), templates['other'])

# --- CORE LOGIC FUNCTIONS ---

async def collect_target_intel(client, target):
    bio = ""
    links = []
    entity = await client.get_entity(target)
    try:
        if isinstance(entity, (types.User, types.Bot)):
            full = await client(GetFullUserRequest(id=entity.id))
            bio = full.full_user.about or ""
        elif isinstance(entity, (types.Chat, types.Channel)):
            full = await client(GetFullChannelRequest(channel=entity.id))
            bio = full.full_chat.about or ""
        links = re.findall(r'(https?://[^\s]+)', bio)
    except Exception:
        pass
    return entity, bio, links

async def join_if_private(client, target):
    if "t.me/+" in target or "t.me/joinchat/" in target:
        hash_code = target.split('/')[-1].replace('+', '')
        try:
            await client(ImportChatInviteRequest(hash_code))
            print(f"{Fore.GREEN}[+] Successfully accessed private entity.")
            await asyncio.sleep(5)
        except errors.UserAlreadyParticipantError:
            pass
        except Exception as e:
            print(f"{Fore.RED}[!] Could not join: {e}")

async def run_termination_sequence(session_name, target, count, mode):
    client = TelegramClient(os.path.join(SESSION_DIR, session_name), API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"{Fore.RED}[!] Session {session_name} invalid. Skipping.")
            return

        await join_if_private(client, target)
        entity, bio, links = await collect_target_intel(client, target)
        legal_msg = generate_legal_report(mode, str(entity.id), bio, links)
        messages = await client.get_messages(entity, limit=25)
        msg_ids = [m.id for m in messages if m.id] if messages else []

        reason_map = {
            'spam': types.InputReportReasonSpam(),
            'violence': types.InputReportReasonViolence(),
            'pornography': types.InputReportReasonPornography(),
            'child_abuse': types.InputReportReasonChildAbuse(),
            'fake_account': types.InputReportReasonFake(),
            'copyright': types.InputReportReasonCopyright(),
            'drugs': types.InputReportReasonIllegalDrugs(),
            'personal_details': types.InputReportReasonGeoIrrelevant(),
            'other': types.InputReportReasonOther()
        }
        selected_reason = reason_map.get(mode.lower(), types.InputReportReasonOther())

        print(f"{Fore.YELLOW}[*] {session_name} is launching legal attack on {type(entity).__name__}...")

        for i in range(1, count + 1):
            try:
                await client(functions.account.ReportPeerRequest(
                    peer=entity, reason=selected_reason, message=legal_msg
                ))
                if msg_ids:
                    await client(functions.messages.ReportRequest(
                        peer=entity, id=msg_ids, reason=selected_reason, message=legal_msg
                    ))

                print(f"{Fore.CYAN}[{session_name}] {Fore.GREEN}Report {i}/{count} Delivered. status: SUCCESS")
                await asyncio.sleep(random.randint(15, 30))

            except errors.FloodWaitError as e:
                print(f"{Fore.RED}[!] Rate Limit hit. Sleeping for {e.seconds}s")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"{Fore.RED}[❌] Batch Failed: {e}")
                break
    finally:
        await client.disconnect()

# --- MAIN INTERFACE ---

async def main():
    # Updated Nobita Banner
    print(f"""{Fore.CYAN}{Style.BRIGHT}
    ███╗   ██╗ ██████╗ ██████╗ ██╗████████╗ █████╗ 
    ████╗  ██║██╔═══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
    ██╔██╗ ██║██║   ██║██████╔╝██║   ██║   ███████║
    ██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██╔══██║
    ██║ ╚████║╚██████╔╝██████╔╝██║   ██║   ██║  ██║
    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝
              {Fore.WHITE}BY NOBITA | ADVANCED TERMINATOR v4.0
    """)

    parser = argparse.ArgumentParser()
    parser.add_argument("-an", "--add_number")
    parser.add_argument("-t", "--target")
    parser.add_argument("-r", "--count", type=int, default=5)
    parser.add_argument("-m", "--mode")
    args = parser.parse_args()

    if args.add_number:
        session_id = f"Ac_{args.add_number[-4:]}"
        client = TelegramClient(os.path.join(SESSION_DIR, session_id), API_ID, API_HASH)
        await client.start(args.add_number)
        print(f"{Fore.GREEN}[V] Account {args.add_number} is now in the Nobita pool.")
        await client.disconnect()
        return

    if args.target and args.mode:
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        if not sessions:
            print(f"{Fore.RED}[!] No accounts found. Use -an to login.")
            return

        print(f"{Fore.MAGENTA}[!] INITIATING SYSTEM TERMINATION SEQUENCE ON: {args.target}")
        for s in sessions:
            s_name = s.replace('.session', '')
            await run_termination_sequence(s_name, args.target, args.count, args.mode)
            print(f"{Fore.BLUE}[i] Account switch in progress... Randomized safety gap.")
            await asyncio.sleep(random.randint(30, 60))
        print(f"{Fore.GREEN}\n[✓] ALL REPORTS SUBMITTED BY NOBITA SYSTEM.")
    else:
        print(f"{Fore.YELLOW}Usage: python3 script.py -t @target -m spam -r 5")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Script stopped by Nobita.")
        sys.exit()
