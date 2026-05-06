#!/usr/bin/env python3
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NOBITA — Telegram Mass Report Engine v4.2 (Verified Edition)
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
VERSION = "4.2"
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

# ─── HUMAN-LIKE MESSAGE POOL ────────────────────────────────────────────────────
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

# ─── BANNER ─────────────────────────────────────────────────────────────────────
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
{Fore.MAGENTA}    >> 10 Report Reasons | Multi-Account | Human-Like <<
{Fore.RESET}"""


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_next_account_number() -> int:
    if not path.exists("sessions"):
        mkdir("sessions")
        return 1
    max_num = 0
    for f in listdir("sessions"):
        match = re.search(r"Ac(\d+)\.session", f)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    return max_num + 1


def get_valid_session_files() -> list:
    if not path.exists("sessions"):
        mkdir("sessions")
        return []
    valid = []
    for f in listdir("sessions"):
        match = re.search(r"Ac(\d+)\.session", f)
        if match:
            valid.append((int(match.group(1)), f))
    valid.sort(key=lambda x: x[0])
    return [f for _, f in valid]


async def perform_extra_human_action(client):
    """Random human-like action to avoid bot detection."""
    roll = random.random()
    try:
        if roll < 0.15:
            await client.get_entity("self")
            await asyncio.sleep(random.uniform(0.5, 2.0))
        elif roll < 0.25:
            await client.get_dialogs(limit=5)
            await asyncio.sleep(random.uniform(0.3, 1.5))
        elif roll < 0.30:
            await asyncio.sleep(random.uniform(2.0, 5.0))
    except Exception:
        pass


async def safe_join_channel(client, target_entity, account_num: int) -> bool:
    """
    Safely handle joining ANY type of target.
    """
    entity_type = "unknown"
    try:
        if hasattr(target_entity, 'broadcast') and target_entity.broadcast:
            entity_type = "channel"
        elif hasattr(target_entity, 'megagroup') and target_entity.megagroup:
            entity_type = "group"
        elif hasattr(target_entity, 'username') and target_entity.username:
            entity_type = "user_or_bot"
    except Exception:
        pass
    
    if entity_type == "user_or_bot":
        return True
    
    already_member = False
    try:
        await client.get_participants(target_entity, limit=1)
        already_member = True
    except Exception:
        pass
    
    if already_member:
        return True
    
    try:
        await client(functions.channels.JoinChannelRequest(target_entity))
        await asyncio.sleep(random.uniform(5.0, 6.5))
        return True
    except Exception:
        return True


# ═══════════════════════════════════════════════════════════════════════════════
#  REPORT WORKER
# ═══════════════════════════════════════════════════════════════════════════════

async def report_worker(
    session_path: str,
    account_num: int,
    target: str,
    reason_class,
    report_count: int,
    results: list,
):
    """Single account worker with full human-like behavior."""
    client = TelegramClient(session_path, API_ID, API_HASH)
    profile = random.choice(TIMING_PROFILES)
    min_delay, max_delay, action_chance = profile
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            results.append({"account": account_num, "success": 0, "total": 0})
            return
        
        me = await client.get_entity("self")
        user_name = me.first_name or me.username or f"User{me.id}"
        
        try:
            target_entity = await client.get_entity(target)
        except Exception as e:
            results.append({"account": account_num, "success": 0, "total": 0})
            return
        
        await safe_join_channel(client, target_entity, account_num)
        
        success = 0
        failed = 0
        
        for i in range(1, report_count + 1):
            try:
                msg = random.choice(REPORT_MESSAGES)
                await client(ReportPeerRequest(peer=target_entity, reason=reason_class(), message=msg))
                success += 1
                print(f" [{Fore.GREEN}✓{Fore.RESET}] Ac{account_num} #{i}/{report_count} REPORTED")
                
                if random.random() < action_chance:
                    await perform_extra_human_action(client)
                
                await asyncio.sleep(random.uniform(min_delay, max_delay))
            except FloodWaitError as e:
                await asyncio.sleep(min(e.seconds + 2, 60))
            except Exception:
                failed += 1
                await asyncio.sleep(2)
        
        results.append({"account": account_num, "success": success, "total": report_count, "failed": failed})
    finally:
        await client.disconnect()


async def orchestrate(target: str, reason_name: str, report_count: int):
    session_files = get_valid_session_files()
    if not session_files: return
    
    reason_class = REASON_MAP.get(reason_name)
    ac = len(session_files)
    
    print(f"\n {Fore.CYAN}══════ RUNNING ATTACK ══════{Fore.RESET}")
    results = []
    tasks = []
    
    for idx, sf in enumerate(session_files, 1):
        tasks.append(report_worker(f"sessions/{sf}", idx, target, reason_class, report_count, results))
        await asyncio.sleep(random.uniform(1.0, 2.5))
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    s = sum(r.get("success", 0) for r in results)
    print(f"\n {Fore.GREEN}Total Successful Reports: {s}{Fore.RESET}")


async def verify_and_confirm(target: str):
    """Fetch target details and ask for user confirmation."""
    session_files = get_valid_session_files()
    if not session_files:
        print(f" [{Fore.RED}!{Fore.RESET}] No sessions found to verify target.")
        return False

    client = TelegramClient(f"sessions/{session_files[0]}", API_ID, API_HASH)
    await client.connect()
    
    try:
        print(f" [{Fore.CYAN}ℹ{Fore.RESET}] Fetching target info...")
        entity = await client.get_entity(target)
        
        # Determine Type and Name
        if isinstance(entity, types.User):
            t_type = "User"
            t_name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
            if entity.bot: t_type = "Bot"
        elif isinstance(entity, types.Channel):
            t_type = "Channel/Group"
            t_name = entity.title
        else:
            t_type = "Unknown"
            t_name = "N/A"

        print(f"\n{Fore.WHITE}┌─── {Fore.YELLOW}TARGET DETAILS {Fore.WHITE}────")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Name:     {Fore.WHITE}{t_name}")
        print(f"{Fore.WHITE}│ {Fore.CYAN}ID:       {Fore.WHITE}{entity.id}")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Username: {Fore.WHITE}@{getattr(entity, 'username', 'None')}")
        print(f"{Fore.WHITE}│ {Fore.CYAN}Type:     {Fore.WHITE}{t_type}")
        print(f"{Fore.WHITE}└───────────────────────────────")
        
        choice = input(f"\nConfirm target? (y/n): ").lower()
        return choice == 'y'
        
    except Exception as e:
        print(f" [{Fore.RED}✗{Fore.RESET}] Error resolving target: {e}")
        return False
    finally:
        await client.disconnect()


def run_multi_reason(target: str, report_count: int, reasons: list):
    async def worker():
        for rn in reasons:
            await orchestrate(target, rn, report_count)
            await asyncio.sleep(5)
    asyncio.run(worker())


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-an", "--add-number")
    parser.add_argument("-r", "--run", type=int)
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-m", "--mode", choices=list(REASON_MAP.keys()) + ["all"])
    parser.add_argument("-re", "--reasons", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    
    args = parser.parse_args()
    print(BANNER)
    
    if args.add_number:
        phone = args.add_number
        num = get_next_account_number()
        client = TelegramClient(f"sessions/Ac{num}", API_ID, API_HASH)
        client.start(phone=phone)
        return

    if args.run and args.target and args.mode:
        target = args.target.lstrip("@")
        
        # NEW VERIFICATION FEATURE
        if not asyncio.run(verify_and_confirm(target)):
            print(f" [{Fore.RED}✗{Fore.RESET}] Aborted.")
            return

        if args.mode == "all":
            run_multi_reason(target, args.run, list(REASON_MAP.keys()))
        else:
            asyncio.run(orchestrate(target, args.mode, args.run))
        return

    print(" Use -h for help.")

if __name__ == "__main__":
    main()
