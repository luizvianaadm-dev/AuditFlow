import subprocess
import sys

def run_command(command, ignore_errors=False):
    """Runs a shell command and prints it."""
    print(f"> {command}")
    try:
        subprocess.check_call(command, shell=True)
        return True
    except subprocess.CalledProcessError:
        if ignore_errors:
            print(f"Command failed: {command}")
            return False
        raise

def get_feature_branches():
    """Fetches and lists all remote feature branches."""
    print("Fetching latest changes from origin...")
    subprocess.run("git fetch origin", shell=True, check=True)
    
    output = subprocess.check_output("git branch -r", shell=True).decode("utf-8")
    branches = []
    for line in output.splitlines():
        line = line.strip()
        if "origin/feature/" in line:
            branches.append(line)
    return branches

def main():
    print("--- AuditFlow Rebase Helper ---")
    branches = get_feature_branches()
    print(f"Found {len(branches)} feature branches to rebase onto origin/main.")
    
    success_count = 0
    fail_count = 0
    
    for remote_branch in branches:
        local_branch = remote_branch.replace("origin/", "")
        print(f"\nProcessing: {local_branch}")
        
        try:
            # 1. Checkout the branch (create local if needed, reset to match remote)
            # Using -B to force reset local to match remote start point matches 'rebase' intent usually
            # But if user has local work, -B might overwrite. 
            # Safer: checkout. If exists, git pull --rebase?
            # User said "branches do Jules", implies we just want to bring them up to date.
            run_command(f"git checkout -B {local_branch} {remote_branch}")
            
            # 2. Rebase onto origin/main
            run_command("git rebase origin/main")
            
            print(f"✅ SUCCESS: {local_branch} rebased.")
            success_count += 1
            
            # Optional: Push?
            # run_command(f"git push origin {local_branch} --force")
            
        except subprocess.CalledProcessError:
            print(f"❌ ERROR: Conflict or failure on {local_branch}. Aborting rebase for this branch.")
            subprocess.run("git rebase --abort", shell=True, stderr=subprocess.DEVNULL)
            fail_count += 1
            
    print(f"\n--- Summary ---")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print("Run 'git push origin <branch> --force' manually for verified branches.")

if __name__ == "__main__":
    main()
