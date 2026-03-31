import asyncio
import os
import argparse
from telethon import TelegramClient, functions, types
from telethon.errors import FloodWaitError, UserAlreadyParticipantError, InviteHashExpiredError
from telethon.tl.functions.messages import ImportChatInviteRequest
from colorama import Fore, init

init(autoreset=True)

# --- CONFIGURATION ---
API_ID = 6432372  # Aap apna API ID yahan badal sakte hain
API_HASH = 'b182390150971c521783f46a7544a658'
SESSION_DIR = 'sessions'

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

async def join_private_chat(client, target):
    """Private link se join karne ka logic"""
    if "t.me/+" in target or "t.me/joinchat/" in target:
        hash_code = target.split('/')[-1].replace('+', '')
        try:
            await client(ImportChatInviteRequest(hash_code))
            print(f"{Fore.GREEN}[+] Joined Private Chat: {target}")
            await asyncio.sleep(2) # Join ke baad thoda gap
            return True
        except UserAlreadyParticipantError:
            return True
        except InviteHashExpiredError:
            print(f"{Fore.RED}[❌] Link Expired: {target}")
            return False
        except Exception as e:
            print(f"{Fore.RED}[❌] Join Error: {e}")
            return False
    return True

async def report_peer(session_name, target, count, mode):
    client = TelegramClient(os.path.join(SESSION_DIR, session_name), API_ID, API_HASH)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"{Fore.RED}[!] Session {session_name} is invalid. Skipping...")
            return

        # Step 1: Auto-Join if Private
        await join_private_chat(client, target)

        # Step 2: Get Entity & Evidence
        try:
            entity = await client.get_entity(target)
            messages = await client.get_messages(entity, limit=5)
            msg_ids = [m.id for m in messages] if messages else []
        except Exception as e:
            print(f"{Fore.RED}[!] Could not fetch entity {target}: {e}")
            return

        # Step 3: Reporting Reasons Mapping
        reasons = {
            'spam': types.InputReportReasonSpam(),
            'violence': types.InputReportReasonViolence(),
            'pornography': types.InputReportReasonPornography(),
            'child_abuse': types.InputReportReasonChildAbuse(),
            'fake_account': types.InputReportReasonFake(),
            'copyright': types.InputReportReasonCopyright(),
        }
        
        selected_reason = reasons.get(mode.lower(), types.InputReportReasonSpam())

        # Step 4: Start Reporting Loop
        for i in range(1, count + 1):
            try:
                # API Level Report with Evidence
                await client(functions.account.ReportPeerRequest(
                    peer=entity,
                    reason=selected_reason,
                    message=f"Urgent: This content violates safety terms - {mode}"
                ))
                
                # If messages exist, report specific messages too
                if msg_ids:
                    await client(functions.messages.ReportRequest(
                        peer=entity,
                        id=msg_ids,
                        reason=selected_reason,
                        message=f"Reporting specific illegal content - {mode}"
                    ))

                print(f"{Fore.CYAN}[{session_name}] {Fore.GREEN}Report {i}/{count} Sent! ✅")
                await asyncio.sleep(5) # Anti-Ban Delay

            except FloodWaitError as e:
                print(f"{Fore.YELLOW}[!] {session_name} Sleeping for {e.seconds}s (FloodWait)")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"{Fore.RED}[❌] Report Failed: {e}")
                break

    finally:
        await client.disconnect()

async def main():
    parser = argparse.ArgumentParser(description="TelReper - Advanced Multi-Account Reporter")
    parser.add_argument("-an", "--add_number", help="Add a new Telegram account")
    parser.add_argument("-t", "--target", help="Target Username or Private Link")
    parser.add_argument("-r", "--count", type=int, help="Number of reports per account")
    parser.add_argument("-m", "--mode", help="Reason (spam, pornography, violence, etc.)")
    
    args = parser.parse_args()

    # Login Logic
    if args.add_number:
        session_id = f"Ac_{args.add_number[-4:]}"
        client = TelegramClient(os.path.join(SESSION_DIR, session_id), API_ID, API_HASH)
        await client.start(args.add_number)
        print(f"{Fore.GREEN}[V] Account {args.add_number} saved as {session_id}")
        await client.disconnect()
        return

    # Reporting Logic
    if args.target and args.count and args.mode:
        sessions = [f for f in os.listdir(SESSION_DIR) if f.endswith('.session')]
        if not sessions:
            print(f"{Fore.RED}[!] No accounts found. Use -an to login first.")
            return

        print(f"{Fore.MAGENTA}Starting attack on {args.target} with {len(sessions)} accounts...")
        tasks = [report_peer(s.replace('.session', ''), args.target, args.count, args.mode) for s in sessions]
        await asyncio.gather(*tasks)
    else:
        print(f"{Fore.YELLOW}Usage: python3 main.py -r 10 -t target -m spam")

if __name__ == "__main__":
    asyncio.run(main())
