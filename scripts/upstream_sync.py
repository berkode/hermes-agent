#!/usr/bin/env python3
"""Monthly hermes upstream sync script."""
import os
import subprocess
import sys

repo = "/Users/morpheus/berkode/hermes-agent"

def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return result

# Step 1: Fetch upstream (disable reflog to avoid permission issues)
print("=== Step 1: Fetch upstream ===")
result = run(["git", "-C", repo, "-c", "core.logAllRefUpdates=false", "fetch", "upstream"])
print(f"RC: {result.returncode}")
print(f"STDOUT: {result.stdout}")
print(f"STDERR: {result.stderr}")

# Step 2: Get current state
print("\n=== Step 2: Check current state ===")
local = run(["git", "-C", repo, "rev-parse", "main"]).stdout.strip()
remote = run(["git", "-C", repo, "rev-parse", "upstream/main"]).stdout.strip()
print(f"Local main:  {local}")
print(f"Remote main: {remote}")

if local == remote:
    print("Already up to date!")
    sys.exit(0)

# Step 3: Check if fast-forward is possible
print("\n=== Step 3: Check fast-forward ===")
result = run(["git", "-C", repo, "merge-base", "--is-ancestor", local, remote])
if result.returncode != 0:
    print("ERROR: Fast-forward not possible. Diverged history.")
    sys.exit(1)
print("Fast-forward is possible.")

# Step 4: Stash local changes
print("\n=== Step 4: Stash local changes ===")
result = run(["git", "-C", repo, "stash", "push", "-m", "auto-stash before upstream sync"])
print(f"RC: {result.returncode}")
print(f"STDOUT: {result.stdout}")
print(f"STDERR: {result.stderr}")

# Step 5: Fast-forward merge
print("\n=== Step 5: Merge upstream/main ===")
result = run(["git", "-C", repo, "-c", "core.logAllRefUpdates=false", "merge", "--ff-only", "upstream/main"])
print(f"RC: {result.returncode}")
print(f"STDOUT: {result.stdout}")
print(f"STDERR: {result.stderr}")
if result.returncode != 0:
    print("ERROR: Merge failed!")
    run(["git", "-C", repo, "stash", "pop"])
    sys.exit(1)

# Step 6: Pop stash
print("\n=== Step 6: Pop stash ===")
result = run(["git", "-C", repo, "stash", "pop"])
print(f"RC: {result.returncode}")
print(f"STDOUT: {result.stdout}")
print(f"STDERR: {result.stderr}")

# Step 7: Push to origin
print("\n=== Step 7: Push to origin ===")
result = run(["git", "-C", repo, "-c", "core.logAllRefUpdates=false", "push", "origin", "main"])
print(f"RC: {result.returncode}")
print(f"STDOUT: {result.stdout}")
print(f"STDERR: {result.stderr}")

# Step 8: Final state
print("\n=== Step 8: Final state ===")
new_local = run(["git", "-C", repo, "rev-parse", "main"]).stdout.strip()
print(f"New main: {new_local}")
log = run(["git", "-C", repo, "log", "--oneline", "-5"]).stdout.strip()
print(f"Recent commits:\n{log}")

# Count new commits
count = run(["git", "-C", repo, "rev-list", "--count", f"{local}..{new_local}"])
print(f"\nNew commits from upstream: {count.stdout.strip()}")
print("\n=== SYNC COMPLETE ===")
