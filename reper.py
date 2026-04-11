import asyncio
import os
import argparse
import random
import re
import sys
from telethon import TelegramClient, functions, types, errors
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.users import GetFullUserRequest
from colorama import Fore, init, Style

init(autoreset=True)

# --- CONFIG ---
API_ID = 20106942 
API_HASH = '3bfe2013e4399af96d78640db6dcd601'
SESSION_DIR = 'sessions'

def generate_legal_report(mode, bot_name, bio, links):
    link_report = f" [Evidence Links: {', '.join(links)}]" if links else ""
    templates = {
        'spam': f"REPORT: Bot {bot_name} is a phishing network. It lures users with 'Viral Content' to steal data via redirects. {link_report}",
        'pornography': f"VIOLATION: Bot {bot_name} is distributing non-consensual viral adult media. {link_report}",
        'child_abuse': f"URGENT: This bot is a distribution hub for prohibited CSAM content. {link_report}",
        'other': f"TOS BREACH: Deceptive practices and illegal content distribution by {bot_name}."
    }
    return templates.get(mode.lower(), templates['spam'])

async def single_sync_report(session_name, target, selected_reason, legal_msg, msg_ids):
    """Parallel Task: Ek hi waqt mein report trigger karega"""
    client = TelegramClient(os.path.join(SESSION_DIR, session_name), API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return f"{Fore.RED}[!] {session_name}: Invalid"

        entity = await client.get_entity(target)
        
        # Ek saath dono tarah ki reports
        await client(ReportPeerRequest(peer=entity, reason=selected_reason, message=legal_msg))
        if msg_ids:
            await client(ReportRequest(peer=entity, id=msg_ids, reason=selected_reason, message=legal_msg))
        
        await client.disconnect()
        return f"{Fore.CYAN}[{session_name}] {Fore.GREEN}SUCCESS ✅"
    except Exception:
        if client: await client.disconnect()
        return f"{Fore.RED}[{session_name}] FAILED ❌"

async def main():
    print(f"""{Fore.CYAN}{Style.BRIGHT}
    ███╗   ██╗ ██████╗ ██████╗ ██╗████████╗ █████╗ 
    ████╗  ██║██╔═══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
    ██╔██╗ ██║██║   ██║██████╔╝██║   ██║   ███████║
    ██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██╔══██║
    ██║ ╚████║╚██████╔╝██████╔╝██║   ██║   ██║  ██║
    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝
              {Fore.WHITE}BY NOBITA | ULTIMATE PARALLEL v8.0
    """)

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target")
    parser.add_argument("-r", "--count", type=int, default=5)
    parser.add_argument("-m", "--mode", default="spam")
    args = parser.parse_args()

    if args.target:
        sessions = [f.replace('.session', '') for f in os.listdir(SESSION_DIR) 
                   if f.endswith('.session') and not f.startswith('Ac_+')]
        
        if not sessions:
            print(f"{Fore.RED}[!] Sessions folder khali hai!"); return

        print(f"{Fore.MAGENTA}[!] PREPARING MASSIVE ATTACK ON: {args.target}")
        
        # Step 1: Suboot jama karna (Intel)
        master = TelegramClient(os.path.join(SESSION_DIR, sessions[0]), API_ID, API_HASH)
        await master.connect()
        entity = await master.get_entity(args.target)
        full = await master(functions.users.GetFullUserRequest(id=entity.id))
        bio = full.full_user.about or ""
        links = re.findall(r'(https?://[^\s]+)', bio)
        msgs = await master.get_messages(entity, limit=15)
        msg_ids = [m.id for m in msgs] if msgs else []
        legal_msg = generate_legal_report(args.mode, args.target, bio, links)
        await master.disconnect()

        reason_map = {
            'spam': types.InputReportReasonSpam(),
            'pornography': types.InputReportReasonPornography(),
            'child_abuse': types.InputReportReasonChildAbuse()
        }
        selected_reason = reason_map.get(args.mode.lower(), types.InputReportReasonOther())

        # Step 2: Parallel Rounds
        for i in range(1, args.count + 1):
            print(f"{Fore.YELLOW}\n>>> ROUND {i}/{args.count} [PARALLEL ATTACK START]")
            
            # Saari IDs ek saath trigger ho rahi hain yahan
            tasks = [single_sync_report(s, args.target, selected_reason, legal_msg, msg_ids) for s in sessions]
            results = await asyncio.gather(*tasks)
            
            for res in results: print(res)
            
            if i < args.count:
                # Chhota sa gap taaki Telegram server block na kare
                print(f"{Fore.BLUE}[i] Next parallel burst in 5s...")
                await asyncio.sleep(5)

        print(f"{Fore.GREEN}\n[✓] {len(sessions)} IDs ne ek saath attack poora kiya!")
    else:
        print(f"{Fore.YELLOW}Usage: python3 reper.py -t @TargetBot -m spam -r 10")

if __name__ == "__main__":
    asyncio.run(main())
