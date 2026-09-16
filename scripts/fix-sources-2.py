import os, re

D = "/mnt/storage/T7data/Projects/m1stykmedia-site-upgrade/src/content/dispatch"

# the-presidents-least-privilege-problem.md: just fix **Report compiled:** line
path = os.path.join(D, "the-presidents-least-privilege-problem.md")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("**Report compiled:** August 10, 2026", "*Report compiled: August 10, 2026.*")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("fixed: the-presidents-least-privilege-problem.md")

# the-phantom-menace: fix final sources block only (last occurrence)
path = os.path.join(D, "the-phantom-menace-far-left-terrorism-framing.md")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = (
    "**Sources:** Center for Strategic and International Studies, NBC News, Axios, FactCheck.org, "
    "PBS NewsHour, The Atlantic, The Washington Post, Reuters, Al Jazeera, Time, CNN, ABC News, "
    "ACLU, Brennan Center, Just Security, Lawfare, House Judiciary Committee Democrats, Stanford Law School, "
    "International Center for Not-for-Profit Law, U.S. Department of State, The White House.\n\n"
    "**Report compiled:** July 2026"
)
new_block = (
    "---\n\n"
    "*Sources: Center for Strategic and International Studies, NBC News, Axios, FactCheck.org, "
    "PBS NewsHour, The Atlantic, The Washington Post, Reuters, Al Jazeera, Time, CNN, ABC News, "
    "ACLU, Brennan Center, Just Security, Lawfare, House Judiciary Committee Democrats, Stanford Law School, "
    "International Center for Not-for-Profit Law, U.S. Department of State, The White House.*\n\n"
    "*Report compiled: July 2026.*"
)
if old_block in content:
    content = content.replace(old_block, new_block, 1)
    print("fixed: the-phantom-menace-far-left-terrorism-framing.md")
else:
    print("NO MATCH: the-phantom-menace-far-left-terrorism-framing.md")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
