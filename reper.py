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

# Initialize Colorama
init(autoreset=True)

# --- CONFIGURATION ---
API_ID = 20106942 
API_HASH = '3bfe2013e4399af96d78640db6dcd601'
SESSION_DIR = 'sessions'

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

# --- FULL LEGAL COMPLAINT GENERATOR ---
def generate_legal_report(mode, entity_name, bio_content, links):
    link_report = f" Detected malicious links: {', '.join(links)}" if links else ""
    templates = {
        'child_abuse': f"URGENT LEGAL NOTICE: This entity ({entity_name}) is involved in the distribution of prohibited CSAM content. International law violation. {link_report}",
        'violence': f"CRITICAL SAFETY WARNING: The entity {entity_name} is actively inciting real-world violence. Public safety risk. {link_report}",
        'pornography': f"POLICY VIOLATION: Non-consensual sexual content distributed by this entity. {link_report}",
        'drugs': f"ILLEGAL TRAFFICKING: Evidence of prohibited substance distribution identified. Bio: {bio_content[:50]}...",
        'personal_details': f"PRIVACY BREACH: This entity is sharing sensitive personal information without consent.",
        'spam': f"DECEPTIVE PRACTICES: This bot/channel is a phishing network using deceptive redirects. {link_report}",
        'fake_account': f"IMPERSONATION FRAUD: Claiming to be an official representative to scam users. {link_report}",
        'other': f"GENERAL TOS VIOLATION: Entity {entity_name} has multiple breaches of guidelines. Bio: {bio_content[:100]}..."
    }
    return templates.get(mode.lower(), templates['other'])

# --- ADVANCED INTEL FUNCTIONS ---
async def collect_target_intel(client, target):
    bio, links = "", []
    try:
        entity = await client.get_entity(target)
        if isinstance(entity, (types.User, types.Bot)):
            full = await client(GetFullUserRequest(id=entity.id))
            bio = full.full_user.about or ""
        elif isinstance(entity, (types.Chat, types.Channel)):
            full = await client(GetFullChannelRequest(channel=entity.id))
            bio = full.full_chat.about or ""
        links = re.findall(r'(https?://[^\s]+)', bio)
        return entity, bio, links
    except:
        return None, "", []

# --- TURBO SYNC REPORTER ---
async def single_sync_report(session_name, target, selected_reason, legal_msg, msg_ids):
    client = TelegramClient(os.path.join(SESSION_DIR, session_name), API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return f"{Fore.RED}[!] {session_name} Invalid/Unauthorized"

        entity = await client.get_entity(target)
        # Peer Report
        await client(functions.account.ReportPeerRequest(peer=entity, reason=selected_reason, message=legal_msg))
        # Evidence Report
        if msg_ids:
            await client(functions.messages.ReportRequest(peer=entity, id=msg_ids, reason=selected_reason, message=legal_msg))
        
        await client.disconnect()
        return f"{Fore.CYAN}[{session_name}] {Fore.GREEN}Report Sent ✅"
    except errors.FloodWaitError as e:
        return f"{Fore.YELLOW}[{session_name}] FloodWait: {e.seconds}s"
    except Exception as e:
        return f"{Fore.RED}[{session_name}] Failed: {str(e)[:20]}"

# --- MAIN INTERFACE ---
async def main():
    print(f"""{Fore.CYAN}{Style.BRIGHT}
    ███╗   ██╗ ██████╗ ██████╗ ██╗████████╗ █████╗ 
    ████╗  ██║██╔═══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
    ██╔██╗ ██║██║   ██║██████╔╝██║   ██║   ███████║
    ██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██╔══██║
    ██║ ╚████║╚██████╔╝██████╔╝██║   ██║   ██║  ██║
    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝
              {Fore.WHITE}BY NOBITA | PRO TURBO SYNC v5.8
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
        print(f"{Fore.GREEN}[V] Account {args.add_number} is now in the pool.")
        await client.disconnect()
        return

    if args.target and args.mode:
        sessions = [f.replace('.session', '') for f in os.listdir(SESSION_DIR) if f.endswith('.session') and "Ac_+" not in f]
        if not sessions:
            print(f"{Fore.RED}[!] No accounts found. Use -an to login."); return

        print(f"{Fore.MAGENTA}[!] INITIATING SYNC ATTACK ON: {args.target}")
        
        # Intel Gathering
        master = TelegramClient(os.path.join(SESSION_DIR, sessions[0]), API_ID, API_HASH)
        await master.connect()
        entity, bio, links = await collect_target_intel(master, args.target)
        msgs = await master.get_messages(entity, limit=15)
        msg_ids = [m.id for m in msgs]
        legal_msg = generate_legal_report(args.mode, str(entity.id if entity else "Target"), bio, links)
        await master.disconnect()

        reason_map = {
            'spam': types.InputReportReasonSpam(), 'violence': types.InputReportReasonViolence(),
            'pornography': types.InputReportReasonPornography(), 'child_abuse': types.InputReportReasonChildAbuse(),
            'fake_account': types.InputReportReasonFake(), 'copyright': types.InputReportReasonCopyright(),
            'drugs': types.InputReportReasonIllegalDrugs(), 'personal_details': types.InputReportReasonGeoIrrelevant(),
            'other': types.InputReportReasonOther()
        }
        selected_reason = reason_map.get(args.mode.lower(), types.InputReportReasonOther())

        for r in range(1, args.count + 1):
            print(f"{Fore.YELLOW}\n>>> ROUND {r} (Syncing {len(sessions)} Accounts)")
            tasks = [single_sync_report(s, args.target, selected_reason, legal_msg, msg_ids) for s in sessions]
            results = await asyncio.gather(*tasks)
            for res in results: print(res)
            
            if r < args.count:
                wait = random.randint(5, 10)
                print(f"{Fore.BLUE}[i] Round complete. Waiting {wait}s...")
                await asyncio.sleep(wait)
        
        print(f"{Fore.GREEN}\n[✓] ALL SYNC ROUNDS COMPLETED.")
    else:
        print(f"{Fore.YELLOW}Usage: python3 reper.py -t @target -m spam -r 5")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit()
