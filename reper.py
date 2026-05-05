#!/usr/bin/env python3
# ─━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  NOBITA — Telegram Mass Report Engine v4.2
#  Author: @Mr3rf1
#  Channel: t.me/Mr3rf1
#  Build: 2026.05.05
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
BUILD = "2026.05.05"

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
    
    - Open channels: joins with 5-6s gap
    - Private channels: skips join, reports anyway
    - Join Request groups: skips join, reports anyway
    - Users/bots: no join needed
    - ANY error: reports still go through
    
    ALWAYS returns True — NEVER blocks reporting.
    """
    
    # ── Detect target type ──
    entity_type = "unknown"
    try:
        if hasattr(target_entity, 'broadcast') and target_entity.broadcast:
            entity_type = "channel"
        elif hasattr(target_entity, 'megagroup') and target_entity.megagroup:
            entity_type = "group"
        elif hasattr(target_entity, 'gigagroup') and target_entity.gigagroup:
            entity_type = "group"
        elif hasattr(target_entity, 'username') and target_entity.username:
            entity_type = "user_or_bot"
        else:
            entity_type = "chat"
    except Exception:
        pass
    
    # ── Users/bots don't need joining ──
    if entity_type == "user_or_bot":
        print(
            f" [{Fore.CYAN}ℹ{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Target is a user — reporting directly"
        )
        await asyncio.sleep(random.uniform(1.0, 2.0))
        return True
    
    # ── Check if already member ──
    already_member = False
    try:
        await client.get_participants(target_entity, limit=1)
        already_member = True
    except Exception:
        pass
    
    if already_member:
        print(
            f" [{Fore.GREEN}✓{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Already a member — no join needed"
        )
        return True
    
    # ── Try to join ──
    try:
        gap = random.uniform(5.0, 6.5)
        print(
            f" [{Fore.CYAN}⏳{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Joining in {gap:.1f}s..."
        )
        await asyncio.sleep(gap)
        
        await client(functions.channels.JoinChannelRequest(target_entity))
        
        post_gap = random.uniform(5.0, 6.5)
        print(
            f" [{Fore.GREEN}✓{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Joined | Waiting {post_gap:.1f}s..."
        )
        await asyncio.sleep(post_gap)
        return True
    
    except UserAlreadyParticipantError:
        return True
    
    except ChannelPrivateError:
        print(
            f" [{Fore.YELLOW}~{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Private channel — {Fore.GREEN}reporting without joining{Fore.RESET}"
        )
        return True
    
    except (InviteHashInvalidError, InviteHashExpiredError):
        print(
            f" [{Fore.YELLOW}~{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Invite invalid — {Fore.GREEN}reporting anyway{Fore.RESET}"
        )
        return True
    
    except ChannelsTooMuchError:
        print(
            f" [{Fore.YELLOW}~{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Too many channels — {Fore.GREEN}reporting anyway{Fore.RESET}"
        )
        return True
    
    except UsersTooMuchError:
        print(
            f" [{Fore.YELLOW}~{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Group full — {Fore.GREEN}reporting anyway{Fore.RESET}"
        )
        return True
    
    except FloodWaitError as e:
        wait = e.seconds
        print(
            f" [{Fore.RED}!{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Join flood {wait}s"
        )
        if wait <= 60:
            await asyncio.sleep(wait + random.uniform(2, 5))
            return True
        print(
            f" [{Fore.YELLOW}~{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"Flood too long — {Fore.GREEN}reporting directly{Fore.RESET}"
        )
        return True
    
    except Exception as e:
        err = str(e).lower()
        # ANY join error — report still goes through
        print(
            f" [{Fore.YELLOW}~{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
            f"{err[:60]} — {Fore.GREEN}reporting anyway{Fore.RESET}"
        )
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
            print(
                f" [{Fore.RED}✗{Fore.RESET}] "
                f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
                f"Not authorized — skipping"
            )
            results.append({"account": account_num, "success": 0, "total": 0})
            return
        
        me = await client.get_entity("self")
        user_name = me.first_name or me.username or f"User{me.id}"
        
        # ── Resolve target ──
        try:
            target_entity = await client.get_entity(target)
        except ValueError:
            print(
                f" [{Fore.RED}✗{Fore.RESET}] "
                f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
                f"Target '{target}' not found"
            )
            results.append({"account": account_num, "success": 0, "total": 0})
            return
        except Exception as e:
            print(
                f" [{Fore.RED}✗{Fore.RESET}] "
                f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
                f"Resolve error: {str(e)[:60]}"
            )
            results.append({"account": account_num, "success": 0, "total": 0})
            return
        
        # ── Safe join (NEVER blocks reporting) ──
        print(
            f" [{Fore.CYAN}ℹ{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET} "
            f"({Fore.GREEN}{user_name}{Fore.RESET}): "
            f"Preparing @{Fore.LIGHTMAGENTA_EX}{target}{Fore.RESET}..."
        )
        await safe_join_channel(client, target_entity, account_num)
        
        print(
            f" [{Fore.CYAN}▶{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET} "
            f"({user_name}): "
            f"{Fore.LIGHTBLUE_EX}{report_count}{Fore.RESET} reports "
            f"[{min_delay}-{max_delay}s profile]"
        )
        
        success = 0
        failed = 0
        
        for i in range(1, report_count + 1):
            try:
                msg = random.choice(REPORT_MESSAGES)
                if random.random() < 0.10:
                    msg += random.choice([
                        " [urgent]", " [review]", " [flagged]", 
                        f" [{random.randint(1000,9999)}]",
                    ])
                
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                result = await client(
                    ReportPeerRequest(
                        peer=target_entity,
                        reason=reason_class(),
                        message=msg,
                    )
                )
                
                if result:
                    success += 1
                    print(
                        f" [{Fore.GREEN}✓{Fore.RESET}] "
                        f"Ac{Fore.YELLOW}{account_num}{Fore.RESET} "
                        f"#{i}/{report_count} REPORTED"
                    )
                else:
                    failed += 1
                    print(
                        f" [{Fore.YELLOW}~{Fore.RESET}] "
                        f"Ac{Fore.YELLOW}{account_num}{Fore.RESET} "
                        f"#{i}/{report_count} no response"
                    )
                
                if random.random() < action_chance:
                    await perform_extra_human_action(client)
                
                delay = random.uniform(min_delay, max_delay) + random.uniform(-0.3, 0.8)
                await asyncio.sleep(max(0.5, delay))
            
            except FloodWaitError as e:
                wait = e.seconds
                print(
                    f" [{Fore.RED}!{Fore.RESET}] "
                    f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
                    f"Flood {wait}s"
                )
                if wait > 180:
                    break
                await asyncio.sleep(min(wait + random.uniform(2, 5), 120))
            
            except (ChannelPrivateError, PeerIdInvalidError):
                print(
                    f" [{Fore.RED}✗{Fore.RESET}] "
                    f"Ac{Fore.YELLOW}{account_num}{Fore.RESET}: "
                    f"Target inaccessible — stopped"
                )
                break
            
            except Exception as e:
                err = str(e)
                if "FLOOD_WAIT" in err:
                    m = re.search(r"(\d+)", err)
                    w = int(m.group(1)) if m else 60
                    await asyncio.sleep(min(w + random.uniform(2, 5), 90))
                else:
                    failed += 1
                    print(
                        f" [{Fore.RED}✗{Fore.RESET}] "
                        f"Ac{Fore.YELLOW}{account_num}{Fore.RESET} "
                        f"#{i}/{report_count} — {err[:70]}"
                    )
                    await asyncio.sleep(random.uniform(2.0, 4.0))
        
        color = Fore.GREEN if success > 0 else Fore.RED
        print(
            f" [{Fore.CYAN}■{Fore.RESET}] "
            f"Ac{Fore.YELLOW}{account_num}{Fore.RESET} "
            f"({user_name}): "
            f"{color}{success}/{report_count}{Fore.RESET} "
            f"ok | {Fore.RED}{failed}{Fore.RESET} fail"
        )
        results.append({
            "account": account_num, "name": user_name,
            "success": success, "total": report_count, "failed": failed,
        })
    
    finally:
        await client.disconnect()


async def orchestrate(target: str, reason_name: str, report_count: int):
    """Run all accounts against target."""
    session_files = get_valid_session_files()
    if not session_files:
        print(f" [{Fore.RED}!{Fore.RESET}] No accounts. Add one: python3 {argv[0]} -an +1234567890")
        return
    
    reason_class = REASON_MAP.get(reason_name)
    if not reason_class:
        print(f" [{Fore.RED}!{Fore.RESET}] Invalid reason: {reason_name}")
        return
    
    ac = len(session_files)
    total = ac * report_count
    
    print(f"\n {Fore.CYAN}═══════════════════════════════════════{Fore.RESET}")
    print(f" {Fore.CYAN}  TARGET:{Fore.RESET}   @{Fore.LIGHTMAGENTA_EX}{target}{Fore.RESET}")
    print(f" {Fore.CYAN}  REASON:{Fore.RESET}   {Fore.YELLOW}{reason_name}{Fore.RESET}")
    print(f" {Fore.CYAN}  ACCOUNTS:{Fore.RESET} {Fore.GREEN}{ac}{Fore.RESET}")
    print(f" {Fore.CYAN}  PER ACC:{Fore.RESET}  {Fore.LIGHTBLUE_EX}{report_count}{Fore.RESET}")
    print(f" {Fore.CYAN}  TOTAL:{Fore.RESET}    {Fore.LIGHTRED_EX}{total}{Fore.RESET}")
    print(f" {Fore.CYAN}  START:{Fore.RESET}    {datetime.now().strftime('%H:%M:%S')}")
    print(f" {Fore.CYAN}═══════════════════════════════════════{Fore.RESET}\n")
    
    results = []
    tasks = []
    
    for idx, sf in enumerate(session_files, 1):
        tasks.append(report_worker(f"sessions/{sf}", idx, target, reason_class, report_count, results))
        await asyncio.sleep(random.uniform(1.5, 3.5))
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # ── Stats ──
    print(f"\n {Fore.GREEN}═══════════════════════════════════════{Fore.RESET}")
    print(f" {Fore.GREEN}  🏁 COMPLETE{Fore.RESET}")
    print(f" {Fore.GREEN}═══════════════════════════════════════{Fore.RESET}")
    
    s = sum(r.get("success", 0) for r in results)
    f = sum(r.get("failed", 0) for r in results)
    t = sum(r.get("total", 0) for r in results)
    
    print(f" {Fore.CYAN}  Target:{Fore.RESET}     @{target}")
    print(f" {Fore.CYAN}  Reason:{Fore.RESET}     {reason_name}")
    print(f" {Fore.CYAN}  Finished:{Fore.RESET}   {datetime.now().strftime('%H:%M:%S')}")
    print(f"  ─────────────────────────────")
    print(f" {Fore.GREEN}  ✅ Sent:{Fore.RESET}       {Fore.LIGHTGREEN_EX}{s}{Fore.RESET}")
    print(f" {Fore.RED}  ❌ Failed:{Fore.RESET}     {Fore.LIGHTRED_EX}{f}{Fore.RESET}")
    
    if t > 0:
        pct = (s / t) * 100
        bar = "█" * int(25 * pct / 100) + "░" * (25 - int(25 * pct / 100))
        print(f" {Fore.CYAN}  Rate:{Fore.RESET}        [{bar}] {pct:.1f}%")
    
    print(f" {Fore.GREEN}═══════════════════════════════════════{Fore.RESET}\n")


def run_multi_reason(target: str, report_count: int, reasons: list):
    """Run all reasons cyclically."""
    async def worker():
        for rn in reasons:
            print(f"\n {Fore.YELLOW}═══ ROUND: {rn.upper()} ═══{Fore.RESET}")
            await orchestrate(target, rn, report_count)
            await asyncio.sleep(random.uniform(3.0, 7.0))
    asyncio.run(worker())


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════════

def show_help():
    print(f"""
{Fore.CYAN}NOBITA v{VERSION} — Help{Fore.RESET}
{Fore.WHITE}──────────────────────────────────────────────{Fore.RESET}

{Fore.YELLOW}ADD ACCOUNT:{Fore.RESET}
  python3 {argv[0]} {Fore.LIGHTBLUE_EX}-an +1234567890{Fore.RESET}

{Fore.YELLOW}REPORT:{Fore.RESET}
  python3 {argv[0]} {Fore.LIGHTBLUE_EX}-r 500 -t user -m spam{Fore.RESET}

{Fore.YELLOW}ARGS:{Fore.RESET}
  {Fore.GREEN}-an{Fore.RESET}   Add phone number
  {Fore.GREEN}-r{Fore.RESET}    Reports per account
  {Fore.GREEN}-t{Fore.RESET}    Target username
  {Fore.GREEN}-m{Fore.RESET}    Reason: spam, fake_account, violence, child_abuse,
             pornography, geoirrelevant, illegal_drugs, other,
             personal_details, all
  {Fore.GREEN}-re{Fore.RESET}   List reasons
  {Fore.GREEN}-h{Fore.RESET}    This help

{Fore.YELLOW}EXAMPLES:{Fore.RESET}
  python3 {argv[0]} -an +911234567890
  python3 {argv[0]} -r 1000 -t badchannel -m spam
  python3 {argv[0]} -r 500 -t target -m all
{Fore.RESET}""")


def show_reasons():
    print(f"""
{Fore.CYAN}NOBITA — Report Reasons{Fore.RESET}
{Fore.WHITE}───────────────────────────────{Fore.RESET}
  spam             → Spam
  fake_account     → Fake / impersonation
  violence         → Violence / threats
  child_abuse      → Child safety
  pornography      → Explicit content
  geoirrelevant    → Geo irrelevant
  illegal_drugs    → Drugs
  other            → Other violations
  personal_details → Doxxing / private info
{Fore.RESET}""")


def main():
    parser = argparse.ArgumentParser(
        description=f"NOBITA Telegram Mass Report Engine v{VERSION}",
        add_help=False,
    )
    parser.add_argument("-an", "--add-number")
    parser.add_argument("-r", "--run", type=int)
    parser.add_argument("-t", "--target", type=str)
    parser.add_argument("-m", "--mode", choices=list(REASON_MAP.keys()) + ["all"])
    parser.add_argument("-re", "--reasons", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    
    args = parser.parse_args()
    
    print(BANNER)
    
    if args.help:
        show_help()
        return
    
    if args.reasons:
        show_reasons()
        return
    
    if args.add_number:
        phone = args.add_number
        num = get_next_account_number()
        session = f"sessions/Ac{num}"
        client = TelegramClient(session, API_ID, API_HASH)
        try:
            print(f" [{Fore.CYAN}ℹ{Fore.RESET}] Adding Ac{num}...")
            print(f" [{Fore.YELLOW}⚠{Fore.RESET}] Check phone for OTP")
            client.start(phone=phone)
            print(f" [{Fore.GREEN}✓{Fore.RESET}] Ac{num} added!")
        except PhoneNumberInvalidError:
            print(f" [{Fore.RED}!{Fore.RESET}] Invalid number. Use: +[code][number]")
        except Exception as e:
            print(f" [{Fore.RED}!{Fore.RESET}] {e}")
        return
    
    if args.run and args.target and args.mode:
        target = args.target.lstrip("@")
        count = args.run
        if args.mode == "all":
            all_r = list(REASON_MAP.keys())
            print(f" [{Fore.MAGENTA}⚡{Fore.RESET}] ALL {len(all_r)} reasons × {count} each")
            run_multi_reason(target, count, all_r)
        else:
            asyncio.run(orchestrate(target, args.mode, count))
        return
    
    print(f" Use --help for commands | {Fore.MAGENTA}t.me/Mr3rf1{Fore.RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n [{Fore.YELLOW}⚠{Fore.RESET}] Interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"\n [{Fore.RED}!{Fore.RESET}] Fatal: {e}")
        sys.exit(1)
