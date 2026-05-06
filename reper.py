#!/usr/bin/env python3
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NOBITA — Telegram Mass Report Engine v4.3 (Full Heavy Edition)
#  Author: @Mr3rf1
#  Channel: t.me/Mr3rf1
#  Build: 2026.05.06
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import asyncio
import argparse
import random
import re
import sys
from datetime import datetime
from os import listdir, mkdir, path
from sys import argv

from colorama import Fore, init
from telethon import TelegramClient, functions, types
from telethon.errors.rpcerrorlist import (
    PhoneNumberInvalidError,
    FloodWaitError,
    ChannelPrivateError,
    PeerIdInvalidError,
    ChannelsTooMuchError,
    InviteHashInvalidError,
    InviteHashExpiredError,
    UserAlreadyParticipantError,
    UsersTooMuchError,
)
from telethon.tl.functions.account import ReportPeerRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import (
    InputReportReasonSpam,
    InputReportReasonFake,
    InputReportReasonViolence,
    InputReportReasonChildAbuse,
    InputReportReasonPornography,
    InputReportReasonGeoIrrelevant,
    InputReportReasonIllegalDrugs,
    InputReportReasonOther,
    InputReportReasonPersonalDetails,
)

# ─── INIT ───────────────────────────────────────────────────────────────────────
init(autoreset=True)
VERSION = "4.3"
BUILD = "2026.05.06"

# ─── CREDENTIALS ────────────────────────────────────────────────────────────────
API_ID = 20106942
API_HASH = "3bfe2013e4399af96d78640db6dcd601"

# ─── REASON MAP ─────────────────────────────────────────────────────────────────
REASON_MAP = {
    "spam":             InputReportReasonSpam,
    "fake_account":     InputReportReasonFake,
    "violence":         InputReportReasonViolence,
    "child_abuse":      InputReportReasonChildAbuse,
    "pornography":      InputReportReasonPornography,
    "geoirrelevant":    InputReportReasonGeoIrrelevant,
    "illegal_drugs":    InputReportReasonIllegalDrugs,
    "other":            InputReportReasonOther,
    "personal_details": InputReportReasonPersonalDetails,
}

# ─── HUMAN-LIKE MESSAGE POOL (Keep it Heavy) ────────────────────────────────────
REPORT_MESSAGES = [
    "This channel is spreading spam and misleading content repeatedly.",
    "Repeated unsolicited promotional content violating TOS.",
    "This account is impersonating a legitimate organization.",
    "Fake identity used to scam users into sharing personal data.",
    "Mass spamming across multiple groups with malicious links.",
    "This channel is a known scam operation targeting Telegram users.",
    "Automated bot-like behavior detected — spam content daily.",
    "Fake giveaways and phishing links posted continuously.",
    "Explicit violent content threatening physical harm to individuals.",
    "This channel glorifies violence and promotes extremist views.",
    "Hate speech inciting violence against specific communities.",
    "Graphic violent imagery posted without any warning.",
    "Direct threats of harm against named individuals.",
    "Promotion of self-harm and violent acts.",
    "Content encouraging terrorism and violent extremism.",
    "Bullying and harassment reaching dangerous levels.",
    "Suspected child exploitation material detected — immediate review needed.",
    "Inappropriate content involving minors being distributed.",
    "This channel shares harmful content targeting underage users.",
    "Predatory behavior detected — minors being contacted inappropriately.",
    "Child safety violation — reporting for urgent moderation.",
    "Underage users exposed to explicit adult content.",
    "Grooming behavior detected in this channel.",
    "Explicit adult content shared without age restriction or warning.",
    "Pornographic materials distributed to unverified audience.",
    "Adult content channel with no age verification mechanism.",
    "Explicit sexual content accessible to minors.",
    "Non-consensual intimate imagery shared publicly.",
    "Pornographic spam targeting random users.",
    "Promotion and sale of illegal narcotics through this channel.",
    "This channel facilitates drug trafficking and distribution.",
    "Content encouraging drug abuse and substance misuse.",
    "Illegal drug marketplace operating openly on Telegram.",
    "Synthetic drugs being advertised with purchase links.",
    "Prescription medication sold without prescription.",
    "Personal information of individuals shared without consent (doxxing).",
    "Private phone numbers, addresses, and IDs publicly exposed.",
    "Sensitive personal data leaked with malicious intent.",
    "Banking details and financial information shared illegally.",
    "Identity theft facilitation — personal docs uploaded.",
    "Private conversations posted without permission.",
    "Repeated violation of Telegram Terms of Service — platform abuse.",
    "Malicious content designed to harm users and reputation.",
    "Automated account used for coordinated abusive behavior.",
    "Harassment campaign targeting innocent Telegram users.",
    "Platform manipulation through fake engagement and bots.",
    "Copyright infringement — stolen content redistributed.",
    "Scam operation defrauding users of money and data.",
    "Coordinated inauthentic behavior across multiple channels.",
]

# ─── HUMAN-LIKE TIMING PROFILES ────────────────────────────────────────────────
TIMING_PROFILES = [
    (2.0, 5.0, 0.3),
    (1.5, 4.0, 0.4),
    (1.0, 3.5, 0.5),
    (2.5, 6.0, 0.2),
    (1.8, 4.5, 0.35),
    (0.8, 2.5, 0.6),
    (3.0, 7.0, 0.15),
    (1.2, 3.0, 0.45),
]

# ─── BANNER (Must stay big) ─────────────────────────────────────────────────────
BANNER = f"""
{Fore.RED}    ███╗   ██╗ ██████╗ ██████╗ ██╗████████╗ █████╗ 
{Fore.RED}    ████╗  ██║██╔═══██╗██╔══██╗██║╚══██╔══╝██╔══██╗
{Fore.RED}    ██╔██╗ ██║██║   ██║██████╔╝██║   ██║   ███████║
{Fore.RED}    ██║╚██╗██║██║   ██║██╔══██╗██║   ██║   ██╔══██║
{Fore.RED}    ██║ ╚████║╚██████╔╝██████╔╝██║   ██║   ██║  ██║
{Fore.RED}    ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝
{Fore.WHITE}    ───────────────────────────────────────────────
{Fore.CYAN}    NOBITA Telegram Mass Report Engine v{VERSION}
{Fore.WHITE}    ───────────────────────────────────────────────
{Fore.YELLOW}    Author: @Mr3rf1          Channel: t.me/Mr3rf1
{Fore.WHITE}    ───────────────────────────────────────────────
{Fore.MAGENTA}    >> Private Link | Parallel Attack | Full Info <<
{Fore.RESET}"""

# ─── UTILITY FUNCTIONS ──────────────────────────────────────────────────────────

def get_next_account_number():
    if not path.exists("sessions"):
        mkdir("sessions")
        return 1
    max_num = 0
    for f in listdir("sessions"):
        match = re.search(r"Ac(\d+)\.session", f)
        if match:
            num = int(match.group(1))
            if num > max_num: max_num = num
    return max_num + 1

def get_valid_session_files():
    if not path.exists("sessions"):
        mkdir("sessions")
        return []
    valid = []
    for f in listdir("sessions"):
        match = re.search(r"Ac(\d+)\.session", f)
        if match: valid.append((int(match.group(1)), f))
    valid.sort(key=lambda x: x[0])
    return [f for _, f in valid]

async def safe_join_logic(client, target, account_num):
    """Logic to join private or public targets."""
    try:
        if "t.me/+" in target or "t.me/joinchat/" in target:
            hash_code = target.split('+')[-1] if '+' in target else target.split('/')[-1]
            await client(ImportChatInviteRequest(hash_code))
            print(f" [{Fore.GREEN}✓{Fore.RESET}] Ac{account_num}: Joined via Private Link")
        else:
            entity = await client.get_entity(target)
            if isinstance(entity, (types.Channel, types.Chat)):
                await client(functions.channels.JoinChannelRequest(entity))
                print(f" [{Fore.GREEN}✓{Fore.RESET}] Ac{account_num}: Joined Public Entity")
    except UserAlreadyParticipantError: pass
    except Exception: pass

# ─── REPORT WORKER ──────────────────────────────────────────────────────────────

async def report_worker(session_path, account_num, target, reason_class, report_count, results):
    client = TelegramClient(session_path, API_ID, API_HASH)
    profile = random.choice(TIMING_PROFILES)
    min_delay, max_delay, action_chance = profile
    
    try:
        await client.connect()
        if not await client.is_user_authorized(): return
        
        # JOIN STEP
        await safe_join_logic(client, target, account_num)
        
        # GET ENTITY
        try:
            target_entity = await client.get_entity(target)
        except Exception: return
        
        success = 0
        for i in range(1, report_count + 1):
            try:
                msg = random.choice(REPORT_MESSAGES)
                await client(ReportPeerRequest(peer=target_entity, reason=reason_class(), message=msg))
                success += 1
                print(f" [{Fore.GREEN}✓{Fore.RESET}] Ac{account_num} REPORTED #{i}/{report_count}")
                await asyncio.sleep(random.uniform(min_delay, max_delay))
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 1)
            except Exception: break
        
        results.append({"account": account_num, "success": success})
    finally:
        await client.disconnect()

# ─── ORCHESTRATOR (Parallel Mode) ───────────────────────────────────────────────

async def orchestrate(target, reason_name, report_count):
    session_files = get_valid_session_files()
    if not session_files: return
    
    reason_class = REASON_MAP.get(reason_name)
    
    print(f"\n {Fore.MAGENTA}⚡ COORDINATED MASS ATTACK STARTING ⚡{Fore.RESET}")
    results = []
    tasks = []
    
    for idx, sf in enumerate(session_files, 1):
        tasks.append(report_worker(f"sessions/{sf}", idx, target, reason_class, report_count, results))
        await asyncio.sleep(0.1) # Tiny stagger to prevent VPS choke
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    s = sum(r.get("success", 0) for r in results)
    print(f"\n {Fore.GREEN}═══ ATTACK FINISHED: Total Reports Sent: {s} ═══{Fore.RESET}")

# ─── VERIFICATION SYSTEM ────────────────────────────────────────────────────────

async def verify_and_confirm(target):
    session_files = get_valid_session_files()
    if not session_files: return False

    client = TelegramClient(f"sessions/{session_files[0]}", API_ID, API_HASH)
    await client.connect()
    
    try:
        print(f" [{Fore.CYAN}ℹ{Fore.RESET}] Fetching target info...")
        entity = await client.get_entity(target)
        
        t_name = getattr(entity, 'title', f"{getattr(entity, 'first_name', '')} {getattr(entity, 'last_name', '')}")
        t_id = entity.id
        t_type = "User"
        if isinstance(entity, types.Channel): t_type = "Channel/Group"
        if getattr(entity, 'bot', False): t_type = "Bot"

        print(f"\n{Fore.WHITE}┌─── {Fore.YELLOW}TARGET VERIFICATION {Fore.WHITE}────")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Name:     {Fore.WHITE}{t_name}")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Chat ID:  {Fore.WHITE}{t_id}")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Link/Tgt: {Fore.WHITE}{target}")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Type:     {Fore.WHITE}{t_type}")
        print(f"{Fore.WHITE}└───────────────────────────────")
        
        confirm = input(f"\nConfirm target details? (y/n): ").lower()
        return confirm == 'y'
    except Exception as e:
        print(f" [{Fore.RED}✗{Fore.RESET}] Error: {e}")
        return False
    finally:
        await client.disconnect()

# ─── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-an", "--add-number")
    parser.add_argument("-r", "--run", type=int)
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-m", "--mode", choices=list(REASON_MAP.keys()) + ["all"])
    
    args = parser.parse_args()
    print(BANNER)
    
    if args.add_number:
        num = get_next_account_number()
        client = TelegramClient(f"sessions/Ac{num}", API_ID, API_HASH)
        client.start(phone=args.add_number)
        return

    if args.run and args.target and args.mode:
        if asyncio.run(verify_and_confirm(args.target)):
            if args.mode == "all":
                for rn in REASON_MAP.keys():
                    asyncio.run(orchestrate(args.target, rn, args.run))
            else:
                asyncio.run(orchestrate(args.target, args.mode, args.run))
        return

    print(" Use -h for help.")

if __name__ == "__main__":
    main()
