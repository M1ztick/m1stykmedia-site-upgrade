import os, re

D = "/mnt/storage/T7data/Projects/m1stykmedia-site-upgrade/src/content/dispatch"

# Each entry: (filename, old_sources_text, new_sources_text)
fixes = [
    (
        "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid.md",
        re.compile(r"Sources:\n\n\[1\].*", re.DOTALL),
        "---\n\n*Sources: Yahoo News; Al Jazeera; PBS NewsHour; Arab News; UN News; Wikipedia \u2014 2025 Gaza Strip aid distribution killings; Human Rights Watch.*",
    ),
    (
        "israels-starvation-of-palestine-40000-babies-at-risk.md",
        re.compile(r"Source:\n\nAl Jazeera.*", re.DOTALL),
        "---\n\n*Sources: Al Jazeera, https://aje.io/f4w0aa*",
    ),
    (
        "metas-troubling-history-with-user-privacy.md",
        re.compile(r"Source:\n\nhttps://www\.bing\.com.*", re.DOTALL),
        "---\n\n*Sources: Public regulatory filings, EU GDPR enforcement records, FTC actions, and aggregated news reporting.*",
    ),
    (
        "the-epstein-jail-video-pt-2-the-dojs-smoking-gun.md",
        re.compile(r"Sources:\nCBS News.*", re.DOTALL),
        "---\n\n*Sources: CBS News investigation on the death of Jeffrey Epstein, including forensic video expert analysis; DOJ Inspector General\u2019s Report on Jeffrey Epstein\u2019s death in federal custody.*",
    ),
    (
        "trumps-crypto-empire-from-white-house-to-wallet.md",
        re.compile(r"References\s*\n.*", re.DOTALL),
        "---\n\n*Sources: Official financial disclosures; House Committee on Financial Services reports; market data on $TRUMP meme coin; legal analysis from Prof. Sarah Williams and Richard Painter; Oxford Law Blog; political statements from Sen. Adam Schiff, Rep. Ruben Gallego, and Elizabeth Warren; foreign emoluments documentation; ethics watchdog reports.*",
    ),
    (
        "the-agentic-ai-era-and-the-new-geopolitical-order.md",
        re.compile(r"\s*Works Cited\n.*", re.DOTALL),
        "\n\n---\n\n*Sources: Stanford HAI 2025 AI Index Report; Penn Wharton Budget Model; McKinsey & Company AI in the Workplace 2025; World Economic Forum Future of Jobs Report; Grand View Research AI Agents Market Report; Precedence Research; IoT Analytics; G2 Global AI Adoption Statistics.*",
    ),
    (
        "the-ai-misalignment-dilemna-the-need-for-global-regulations.md",
        re.compile(r"What do you think\? Drop your thoughts.*", re.DOTALL),
        "---\n\n*Sources: Leonard Dung, \u201cCurrent Cases of AI Misalignment and Their Implications for Future Risks.\u201d*",
    ),
]

for filename, pattern, replacement in fixes:
    path = os.path.join(D, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    new_content, count = pattern.subn(replacement, content)
    if count:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"fixed: {filename}")
    else:
        print(f"NO MATCH: {filename}")
