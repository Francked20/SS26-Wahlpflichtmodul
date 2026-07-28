import argparse
import os

from pymongo import MongoClient  # pip install pymongo

# Why this script exists:
# core/site/website/engine/tasks/meta.py's MetaTask hashes each task's full
# serialized content and, if a task's checksum no longer matches anything
# currently registered, deletes and recreates its `challenges` document with
# a fresh ObjectId. Any `user_challenges` (RunningChallenge) doc created
# before that edit still points (via DBRef) at the old, now-deleted
# ObjectId - the backend crashes with AttributeError on 'NoneType' when it
# tries to resolve that link. Editing task content in custom/sites/tasks/
# while a test user already has progress on that day reliably triggers this.
# Fix: delete that user's (or all users') RunningChallenge docs for the
# affected day, so they get recreated fresh against the current challenges.

# How to use (mongo's 27017 is published to the host for local dev, see
# DUMMY_CTF/CLAUDE.md):
# python reset_task_progress.py --day 3
# python reset_task_progress.py --day 3 --username D3f@nzor
# python reset_task_progress.py --day 3 --dry_run

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "admin")
MONGO_DB = os.getenv("MONGO_DB", "ctf_database")


def main():
    parser = argparse.ArgumentParser(
        description="Reset RunningChallenge (user_challenges) progress for a day, "
                     "so stale DBRef links to recreated challenge docs get cleared."
    )
    parser.add_argument("--day", type=int, required=True, help="day_id to reset")
    parser.add_argument("--username", help="only reset this user (default: all users)")
    parser.add_argument("--dry_run", action="store_true", help="show what would be deleted, don't delete")
    args = parser.parse_args()

    client = MongoClient(
        host=MONGO_HOST, port=MONGO_PORT,
        username=MONGO_USER, password=MONGO_PASSWORD,
        authSource="admin",
    )
    db = client[MONGO_DB]

    query = {"day_id": args.day}
    if args.username:
        query["username"] = args.username.lower()

    matches = list(db.user_challenges.find(query, {"_id": 1, "username": 1, "task_id": 1}))
    print(f"{len(matches)} user_challenges doc(s) match day_id={args.day}"
          + (f", username={args.username.lower()}" if args.username else ""))
    for m in matches:
        print(f"  - {m['username']} / task_id={m['task_id']}")

    if args.dry_run:
        print("Dry run, nothing deleted.")
        return

    if matches:
        result = db.user_challenges.delete_many(query)
        print(f"Deleted {result.deleted_count} doc(s).")


if __name__ == "__main__":
    main()
