import os

path = "/mnt/storage/T7data/Projects/m1stykmedia-site-upgrade/src/content/dispatch/the-justice-departments-selective-incompetence.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the start of the sources block
marker = "Sources:\n"
idx = content.rfind(marker)
if idx == -1:
    print("marker not found")
else:
    new_sources = (
        "---\n\n"
        "*Sources: NBC News, \u201cJudge seeks to shield Epstein victims after dozens of names exposed in DOJ, estate files\u201d (Nov. 27, 2025); "
        "ABC News, \u201cLaw firm representing alleged Epstein victims sends scathing letter to DOJ\u201d (Nov. 26, 2025); "
        "Wall Street Journal, \u201cDozens of Epstein Victims\u2019 Names Exposed in Files Released by Congress\u201d (Nov. 26, 2025).*"
    )
    content = content[:idx] + new_sources
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("done")
