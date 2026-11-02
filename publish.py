"""Build the academic homepage and publish it using the existing Git login."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parent
REMOTE = "https://github.com/Supradax/yunfengliao.github.io.git"
BRANCH = "master"
WEBSITE = "https://supradax.github.io/yunfengliao.github.io/"

class LocalReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ("src", "href") or not value:
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            self.paths.add(unquote(parsed.path))

def payload_files(root):
    files = {"index.html", "styles.css", "site.js", "content.json", "update.py",
             "update.cmd", "publish.py", "publish.cmd", "preview.cmd", "README.md",
             ".nojekyll", ".gitignore"}
    parser = LocalReferences()
    parser.feed((root / "index.html").read_text(encoding="utf-8"))
    files.update(parser.paths)
    manifest = root / "redirects.json"
    if manifest.is_file():
        redirects = json.loads(manifest.read_text(encoding="utf-8"))
        if not isinstance(redirects.get("paths"), list) or any(not isinstance(name, str) for name in redirects["paths"]):
            raise ValueError("redirects.json paths must be a list of local file paths")
        files.update({"redirects.json", "404.html"})
        files.update(redirects["paths"])
    files.update(file.name for file in root.glob("google*.html"))
    for name in sorted(files):
        path = (root / name).resolve()
        if path == root.resolve() or not path.is_relative_to(root.resolve()) or ".git" in Path(name).parts:
            raise ValueError("Unsafe local asset path: " + name)
        if not path.is_file():
            raise ValueError("Missing website file: " + name)
    return sorted(files)

def system_proxy():
    # Use the current Windows proxy instead of the stale proxy in Git's global config.
    if os.name != "nt":
        return None
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
        try:
            enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
            value = winreg.QueryValueEx(key, "ProxyServer")[0]
        except FileNotFoundError:
            return None
    if not enabled or not value:
        return None
    if "=" in value:
        choices = dict(part.split("=", 1) for part in value.split(";") if "=" in part)
        value = choices.get("https") or choices.get("http")
    if value and "://" not in value:
        value = "http://" + value
    return value

def main():
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument("--check", action="store_true", help="Build and validate files without committing or pushing")
    args = options.parse_args()
    print("[1/5] Updating index.html from content.json...", flush=True)
    subprocess.run([sys.executable, str(ROOT / "update.py")], cwd=ROOT, check=True)
    files = payload_files(ROOT)
    print(f"Validated {len(files)} website files (including referenced images and PDFs).", flush=True)
    if args.check:
        print("Check passed. Nothing was committed or pushed.")
        return
    git = shutil.which("git")
    if not git:
        raise ValueError("Git was not found. Install Git for Windows, then try again.")
    proxy = system_proxy()
    configs = ["-c", "http.version=HTTP/1.1"]
    if proxy:
        configs += ["-c", "http.proxy=" + proxy]
        print("Using the current Windows system proxy for this publish only.")
    env = os.environ.copy()
    env.pop("GIT_SSL_NO_VERIFY", None)
    env.setdefault("GIT_TERMINAL_PROMPT", "1")
    def run(*arguments, cwd=None, capture=True, allow_failure=False):
        command = [git, *configs, *arguments]
        result = subprocess.run(command, cwd=cwd, env=env, text=True,
                                stdout=subprocess.PIPE if capture else None,
                                stderr=subprocess.PIPE if capture else None)
        if result.returncode and not allow_failure:
            # Git output contains no credentials; never read or print stored tokens.
            raise ValueError((result.stderr or result.stdout or "Git command failed.").strip())
        return result
    print("[2/5] Checking the publishing checkout...", flush=True)
    in_repo = (ROOT / ".git").exists()
    checkout = ROOT if in_repo else ROOT.parent / "github-publish"
    if not (checkout / ".git").exists():
        if checkout.exists() and any(checkout.iterdir()):
            raise ValueError("Publishing folder is not an empty folder or a Git checkout: " + str(checkout))
        run("clone", "--depth", "1", "--branch", BRANCH, REMOTE, str(checkout), capture=False)
    remote = run("remote", "get-url", "origin", cwd=checkout).stdout.strip()
    if remote.rstrip("/").removesuffix(".git") != REMOTE.removesuffix(".git"):
        raise ValueError("The publishing checkout points to a different repository. Nothing was pushed.")
    branch = run("branch", "--show-current", cwd=checkout).stdout.strip()
    if branch != BRANCH:
        raise ValueError("Expected branch master. Nothing was pushed.")
    dirty = run("status", "--porcelain", cwd=checkout).stdout
    if not in_repo and dirty:
        raise ValueError("The separate publishing checkout has uncommitted changes. Resolve them first: " + str(checkout))
    if in_repo:
        changed = set()
        for arguments in (("diff", "--name-only"), ("diff", "--cached", "--name-only"), ("ls-files", "--others", "--exclude-standard")):
            changed.update(run(*arguments, cwd=checkout).stdout.splitlines())
        if changed.difference(files):
            raise ValueError("There are unrelated modified files. Commit or move them before publishing.")
    print("[3/5] Checking GitHub for newer changes...", flush=True)
    run("fetch", "origin", BRANCH, cwd=checkout, capture=False)
    head = run("rev-parse", "HEAD", cwd=checkout).stdout.strip()
    remote_head = run("rev-parse", "origin/" + BRANCH, cwd=checkout).stdout.strip()
    if head != remote_head:
        ancestor = run("merge-base", "--is-ancestor", remote_head, head, cwd=checkout, allow_failure=True)
        if ancestor.returncode:
            raise ValueError("GitHub has newer or conflicting changes. Sync them first; this script never force-pushes or overwrites them.")
        print("A local commit is waiting to be pushed; it will be included.")
    print("[4/5] Preparing the website commit...", flush=True)
    if not in_repo:
        for name in files:
            target = checkout / name
            if not target.resolve().is_relative_to(checkout.resolve()):
                raise ValueError("Publishing target escapes checkout: " + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, target)
    run("add", "--", *files, cwd=checkout)
    changes = run("diff", "--cached", "--quiet", cwd=checkout, allow_failure=True)
    if changes.returncode == 1:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        run("commit", "-m", "Update academic homepage " + stamp, cwd=checkout, capture=False)
    elif changes.returncode:
        raise ValueError("Could not inspect staged changes. Nothing was pushed.")
    else:
        print("Website files are already up to date.")
    print("[5/5] Pushing to GitHub...", flush=True)
    run("push", "origin", BRANCH, cwd=checkout, capture=False)
    commit = run("rev-parse", "--short", "HEAD", cwd=checkout).stdout.strip()
    print("\nSUCCESS: pushed commit " + commit)
    print("GitHub Pages will deploy it automatically; pushing is not the same as deployment completion.")
    print("Website: " + WEBSITE)
    print("Deployment status: https://github.com/Supradax/yunfengliao.github.io/actions")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("\nPublish stopped: " + str(error), file=sys.stderr)
        print("Your source files are preserved. No force push or reset was performed.", file=sys.stderr)
        sys.exit(1)
