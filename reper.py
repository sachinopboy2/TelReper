import asyncio
import os
import random
import re
import sys
from telethon import TelegramClient, types, errors
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.channels import JoinChannelRequest
from colorama import Fore, init, Style

init(autoreset=True)

# --- API CONFIG ---
API_ID = 20106942 
API_HASH = '3bfe2013e4399af96d78640db6dcd601'
SESSION_DIR = 'sessions'

# Advanced Device List for Hard Spoofing
MODERN_DEVICES = [
    {'device': 'Google Pixel 8 Pro', 'sys': 'Android 14'},
    {'device': 'iPhone 15 Pro Max', 'sys': 'iOS 17.4'},
    {'device': 'Samsung Galaxy S24 Ultra', 'sys': 'Android 14'},
    {'device': 'Xiaomi 14 Ultra', 'sys': 'Android 13'},
    {'device': 'OnePlus 12', 'sys': 'Android 14'},
    {'device': 'iPad Pro M2', 'sys': 'iPadOS 17.1'}
]

def get_banner():
    return f"""{Fore.RED}{Style.BRIGHT}
    ███╗   ██╗ ██████╗ ██████╗ ██╗████████╗ █████╗ 
    ████╗  ██║██╔═══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
    ██╔██╗ ██║██║   ██║██████╔╝██║   ██║   ███████║
    ██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██╔══██║
    ██║ ╚████║╚██████╔╝██████╔╝██║   ██║   ██║  ██║
    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝
    {Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    {Fore.WHITE}       DEVELOPER: {Fore.YELLOW}NOBITA (VORTEX)
    {Fore.WHITE}       TELEGRAM ID: {Fore.GREEN}7081885854
    {Fore.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """

async def report_worker(index, session_name, target, reason, report_msg, msg_ids, is_private):
    # Har session ko ek alag modern device assign karna
    dev_info = random.choice(MODERN_DEVICES)
    
    client = TelegramClient(
        os.path.join(SESSION_DIR, session_name), 
        API_ID, API_HASH,
        device_model=dev_info['device'],
        system_version=dev_info['sys'],
        app_version="10.8.1"
    )
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            return f"{Fore.RED}[{index}] {session_name}: Invalid Session ❌"

        # Private links join logic
        if is_private and ("t.me/+" in target or "t.me/joinchat/" in target):
            try: await client(JoinChannelRequest(target))
            except: pass

        entity = await client.get_entity(target)
        
        # 1. Profile/Account Report
        await client(ReportPeerRequest(peer=entity, reason=reason, message=report_msg))
        
        # 2. Evidence Message Report (Hard Impact)
        if msg_ids:
            # Batch report messages for evidence
            await client(ReportRequest(peer=entity, id=msg_ids, reason=reason, message=report_msg))

        await client.disconnect()
        return f"{Fore.CYAN}[{index}] {Fore.WHITE}{session_name} {Fore.GREEN}SUCCESS ✅ {Fore.LIGHTBLACK_EX}({dev_info['device']})"
    
    except errors.FloodWaitError as e:
        return f"{Fore.YELLOW}[{index}] {session_name}: FloodWait {e.seconds}s"
    except Exception as e:
        return f"{Fore.RED}[{index}] {session_name}: Failed ({type(e).__name__}) ❌"

async def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(get_banner())

    # --- STEP 1: TARGET TYPE ---
    print(f"{Fore.MAGENTA}[+] SELECT TARGET TYPE:")
    print("1. User/Bot (@username)")
    print("2. Public Channel/Group (@link)")
    print("3. Private Channel/Group (Invite Link)")
    t_choice = input(f"{Fore.YELLOW}Choice (1-3): ")
    target = input(f"{Fore.YELLOW}Enter Target/Link: ")

    # --- STEP 2: REASON & FORM ---
    print(f"\n{Fore.MAGENTA}[+] SELECT REPORT REASON:")
    print("1. Spam (Phishing & Bots)\n2. Pornography (Illegal Adult Content)\n3. Child Abuse (Urgent/CSAM)\n4. Fraud (Scam/Copyright)\n5. Violence (Hate Speech)")
    r_choice = input(f"{Fore.YELLOW}Choice (1-5): ")

    # Bada aur Hard Report Message (Report Form)
    report_forms = {
        '1': "LEGAL REPORT: Coordinated spam network detected. This entity is spreading malicious phishing links, automated bot spam, and violating Telegram's API Terms of Service. Immediate termination required to protect the community.",
        '2': "VIOLATION NOTICE: This account/channel is distributing non-consensual and prohibited pornographic material. This is a direct breach of Safety Guidelines regarding adult content distribution.",
        '3': "CRITICAL URGENT REPORT: Prohibited CSAM material detected. This entity is acting as a distribution hub for illegal child safety violations. This requires immediate suspension under international safety laws.",
        '4': "FRAUD ALERT: Systematic financial fraud and deceptive practices. This account is luring users into crypto scams and phishing operations to steal personal data and funds.",
        '5': "SAFETY BREACH: Coordination of violent threats and promotion of hate speech. This entity is inciting harm and violating the fundamental community standards of Telegram."
    }
    legal_msg = report_forms.get(r_choice, "General Violation: Breach of Telegram Terms of Service and Safety Regulations.")

    # --- STEP 3: ATTACK CONFIG ---
    print(f"\n{Fore.MAGENTA}[+] ATTACK CONFIGURATION:")
    num_ids_input = input(f"{Fore.YELLOW}How many IDs to use? (Blank = All): ")
    rounds = int(input(f"{Fore.YELLOW}How many rounds of attack?: ") or 1)

    all_sessions = [f.replace('.session', '') for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
    if not all_sessions:
        print(f"{Fore.RED}[!] Sessions folder khali hai!"); return

    if num_ids_input.isdigit():
        sessions = all_sessions[:int(num_ids_input)]
    else:
        sessions = all_sessions

    # Map Reason
    reason_map = {
        '1': types.InputReportReasonSpam(),
        '2': types.InputReportReasonPornography(),
        '3': types.InputReportReasonChildAbuse(),
        '4': types.InputReportReasonCopyright(),
        '5': types.InputReportReasonViolence()
    }
    selected_reason = reason_map.get(r_choice, types.InputReportReasonOther())

    # Evidence Scraping
    print(f"\n{Fore.BLUE}[*] Gathering evidence from {target}...")
    master = TelegramClient(os.path.join(SESSION_DIR, sessions[0]), API_ID, API_HASH)
    msg_ids = []
    try:
        await master.connect()
        is_private = True if t_choice == '3' else False
        if is_private:
            try: await master(JoinChannelRequest(target))
            except: pass
        
        m_list = await master.get_messages(target, limit=15)
        msg_ids = [m.id for m in m_list]
        await master.disconnect()
    except: pass

    # --- STEP 4: EXECUTION ---
    print(f"\n{Fore.GREEN}🚀 NOBITA MASS REPORTER LAUNCHED ON: {target}")
    print(f"{Fore.WHITE}IDs: {len(sessions)} | Rounds: {rounds}\n")

    for r in range(rounds):
        print(f"{Fore.MAGENTA}--- ATTACK WAVE {r+1} (SIMULTANEOUS) ---")
        
        tasks = []
        for i, s in enumerate(sessions, 1):
            tasks.append(report_worker(i, s, target, selected_reason, legal_msg, msg_ids, (t_choice == '3')))
        
        # Saari IDs ek hi microsecond mein trigger hongi
        results = await asyncio.gather(*tasks)
        
        # Output sequential dikhega (1, 2, 3...)
        for res in results:
            print(res)
            await asyncio.sleep(0.04)

        if r < rounds - 1:
            print(f"\n{Fore.YELLOW}[!] Cooling down for 12 seconds...")
            await asyncio.sleep(12)

    print(f"\n{Fore.GREEN}[🏁] ATTACK COMPLETED. TARGET REPORTED {len(sessions) * rounds} TIMES.")

if __name__ == "__main__":
    asyncio.run(main())
    
