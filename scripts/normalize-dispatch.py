#!/usr/bin/env python3
"""
Normalize every Dispatch article onto the canonical format defined in
`.amazonq/rules/dispatch-format.md`.

Three passes per file:

  1. Frontmatter  — rewritten from META in canonical key order with a clean
                    `description`, `category`, `subject` and kebab-case block
                    tags. `pubDate` is reduced to a bare `YYYY-MM-DD`.
  2. Body         — the duplicate leading title/deck is removed, plain-text
                    section labels are promoted to `## `, numeric / roman
                    enumerators and `**` wrappers are stripped from headings,
                    heading levels are lifted so the first section is always
                    `##`, and stray rules / signatures are dropped.
  3. Sources      — the trailing sources block is rebuilt as
                    `---` + `## Sources` + (italic paragraph | bullet list).

Run from the repo root:  python3 scripts/normalize-dispatch.py
"""

import glob
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("PyYAML is required: pip install pyyaml")

D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "src", "content", "dispatch")

# --------------------------------------------------------------------------
# Per-file metadata. `drop` = raw leading lines to delete (duplicate titles /
# decks). `promote` = plain-text section labels to re-grade as `## ` headings.
# --------------------------------------------------------------------------
META = {
    "billionaire-buy-in-american-electoral-mythos.md": dict(
        title="Billionaire Buy-In: The American Electoral Mythos",
        description="The idea that anyone can become president is a defining "
                    "American myth. The modern campaign landscape tells a different "
                    "story: viability is purchased, and the price of admission is "
                    "set by a donor class the electorate never chose.",
        category="analysis", subject="domestic-politics", featured=False,
        tags=["campaign-finance", "citizens-united", "dark-money",
              "elections", "elites", "representation"],
    ),
    "chatgpt-creates-throne-portrait-my-digital-transformation.md": dict(
        title="ChatGPT Creates a Throne Portrait",
        description="I asked ChatGPT how I would look on a throne, and it rendered "
                    "the answer. A short note on the small, strange pleasures of the "
                    "generative age.",
        category="essay", subject="technology", featured=False,
        tags=["artificial-intelligence", "chat-gpt", "generative-ai", "images"],
    ),
    "chatgpt-prompted-stand-up-comedian-hilarious.md": dict(
        title="ChatGPT Prompted a Stand-Up Comedian",
        description="A custom chatbot built to tell jokes takes the stage and runs a "
                    "set on cryptocurrency, ego, and the modern economy of vibes.",
        category="essay", subject="media-culture", featured=False,
        tags=["artificial-intelligence", "chat-gpt", "custom-chatbots", "comedy"],
    ),
    "chinas-ai-sports-bots-a-cover-for-military-innovation.md": dict(
        title="China's AI Sports Bots: A Cover for Military Innovation",
        description="China's humanoid sports robots may be less about athletic "
                    "prowess than about testing real-time decision-making for the "
                    "battlefield—sold to the public as a safety program.",
        category="analysis", subject="technology", featured=False,
        tags=["artificial-intelligence", "china", "robotics", "military-innovation"],
    ),
    "cia-origins.md": dict(
        title="How the CIA Was Born: From OSS to Cold War Shadow War",
        description="A concise history of the CIA's creation—from the wartime OSS "
                    "and Truman's Central Intelligence Group to the National Security "
                    "Act of 1947 and the early scandals that defined the agency.",
        category="analysis", subject="history", featured=False,
        tags=["cia", "oss", "william-donovan", "harry-truman",
              "national-security-act-1947", "cold-war", "covert-action", "mkultra"],
    ),
    "circles-in-the-grain-the-latest-global-crop-circle-season.md": dict(
        title="Circles in the Grain: The Global Crop Circle Season",
        description="A dispatch on the 2025 crop circle season—the geometry of modern "
                    "formations, the evidence problem, and the competing theories "
                    "behind who, or what, draws in the grain.",
        category="analysis", subject="media-culture", featured=False,
        tags=["crop-circles", "land-art", "folklore", "science-culture"],
    ),
    "human-beats-ai-in-10-hour-coding-marathon-heres-how.md": dict(
        title="Human Beats AI in a 10-Hour Coding Marathon",
        description="At the AtCoder World Tour Finals, a human competitor outlasted "
                    "OpenAI's system across ten hours of programming. What the upset "
                    "does—and doesn't—say about machine intelligence.",
        category="analysis", subject="technology", featured=False,
        tags=["artificial-intelligence", "openai", "competitive-programming",
              "automation"],
    ),
    "iran-hormuz-tanker-attacks-us-retaliation-mou-unravels.md": dict(
        title="Iran Strikes Tankers, the US Retaliates, and the MOU Unravels",
        description="A breakdown of Iran's attacks on commercial shipping in the "
                    "Strait of Hormuz, the US military response, and what it means "
                    "for an already-fraying ceasefire.",
        category="investigation", subject="world-affairs", featured=False,
        tags=["iran", "strait-of-hormuz", "oil-and-gas", "us-foreign-policy",
              "middle-east", "geopolitics"],
    ),
    "israeli-security-cabinets-decision-on-gaza.md": dict(
        title="Israel's Security Cabinet Approves the Occupation of Gaza City",
        description="Israel's security cabinet has approved a plan to take control of "
                    "Gaza City—an escalation that opens the door to further military "
                    "operations with little planning for what follows.",
        category="analysis", subject="world-affairs", featured=False,
        tags=["gaza", "israel-hamas-war", "humanitarian-crises", "international-law"],
    ),
    "israels-starvation-of-palestine-40000-babies-at-risk.md": dict(
        title="Israel's Starvation of Palestine: 40,000 Babies at Risk",
        description="As Israel's blockade tightens, infants are dying of malnutrition "
                    "and Gaza's government warns that 40,000 babies are at risk.",
        category="essay", subject="world-affairs", featured=False,
        tags=["gaza", "famine", "humanitarian-crises", "israeli-war-crimes"],
    ),
    "metas-troubling-history-with-user-privacy.md": dict(
        title="Meta's Troubling History with User Privacy",
        description="From undisclosed tracking to record GDPR fines and child-safety "
                    "suits, Meta's record on user privacy is a decade-long pattern "
                    "rather than a run of accidents.",
        category="analysis", subject="surveillance-state", featured=False,
        tags=["meta", "privacy", "big-tech", "gdpr", "user-data"],
    ),
    "palantir-expanding-shadow.md": dict(
        title="Palantir: The Expanding Shadow of the Surveillance State",
        description="Palantir's origins, its founder's ideological motivations, its "
                    "intelligence pedigree, and what its systems mean for ordinary "
                    "people caught in the widening web of government AI.",
        category="investigation", subject="surveillance-state", featured=False,
        tags=["palantir", "surveillance", "civil-liberties", "ice",
              "peter-thiel", "ai-regulation"],
    ),
    "project-2025-the-conspiracy-that-isnt-a-theory.md": dict(
        title="Project 2025: The Conspiracy That Isn't a Theory",
        description="Project 2025 is not a think-tank wish list—it is an installation "
                    "guide for executive supremacy, and roughly half of it is already "
                    "in force.",
        category="investigation", subject="domestic-politics", featured=False,
        tags=["project-2025", "heritage-foundation", "authoritarianism",
              "civil-service", "executive-power"],
    ),
    "the-agentic-ai-era-and-the-new-geopolitical-order.md": dict(
        title="The Agentic AI Era and the New Geopolitical Order",
        description="The next decade of global competition will turn less on who owns "
                    "the largest models than on which nations can weave autonomous "
                    "agents into their economies first.",
        category="analysis", subject="technology", featured=False,
        tags=["artificial-intelligence", "ai-agents", "geopolitics",
              "digital-sovereignty", "automation"],
    ),
    "the-ai-misalignment-dilemna-the-need-for-global-regulations.md": dict(
        title="The AI Misalignment Dilemma and the Need for Global Regulation",
        description="Documented cases of AI misalignment show the risk is present, not "
                    "hypothetical. Without binding global rules, the companies "
                    "building these systems are grading their own homework.",
        category="analysis", subject="technology", featured=False,
        tags=["artificial-intelligence", "ai-safety", "ai-misalignment",
              "regulation", "big-tech"],
    ),
    "the-bis-and-the-finternet-deep-dive.md": dict(
        title="The BIS and the Finternet: A Deep Dive",
        description="An investigation into the Bank for International Settlements—who "
                    "runs it, what power it wields, and the tokenized, programmable "
                    "'finternet' it is building for the next generation of money.",
        category="investigation", subject="global-finance", featured=False,
        tags=["bis", "central-banking", "cbdc", "finternet", "digital-currency",
              "financial-control"],
    ),
    "the-epstein-jail-video-pt-2-the-dojs-smoking-gun.md": dict(
        title="The Epstein Jail Video, Part 2: The DOJ's Smoking Gun",
        description="Federal officials called the Epstein jailhouse video airtight. A "
                    "closer look at the footage—its missing minute, its editing menu, "
                    "its unrecorded call—suggests otherwise.",
        category="analysis", subject="domestic-politics", featured=False,
        tags=["epstein", "department-of-justice", "coverup", "evidence", "doj"],
    ),
    "the-global-financial-architecture-who-pulls-the-levers.md": dict(
        title="The Architecture of Global Finance: Who Holds the Levers",
        description="A top-down map of the institutions that move money and set "
                    "policy—and the structural flaws engineered beneath the surface.",
        category="investigation", subject="global-finance", featured=False,
        tags=["global-finance", "central-banking", "imf", "blackrock",
              "petrodollar", "wealth-inequality"],
    ),
    "the-integration-trap.md": dict(
        title="The Integration Trap: Congress and the Israeli Defense Industry",
        description="Section 224 of the FY2027 NDAA would structurally fuse the "
                    "American and Israeli defense industries—with no human-rights "
                    "conditionality and no mechanism for accountability.",
        category="investigation", subject="domestic-politics", featured=True,
        tags=["ndaa", "israel", "defense-industry", "lobbying", "icc",
              "military-industrial-complex"],
    ),
    "the-iran-war-profit-sheet.md": dict(
        title="The Iran War Profit Sheet: Who Makes Money When Missiles Fly",
        description="Since the war began, defense contractors have added billions in "
                    "market cap and oil majors have doubled profits. The cost is borne "
                    "by civilians and at the gas pump.",
        category="investigation", subject="global-finance", featured=True,
        tags=["iran-war", "defense-contractors", "military-industrial-complex",
              "oil-profits", "arms-sales"],
    ),
    "the-iran-war-windfall.md": dict(
        title="The Iran War Windfall",
        description="A survey of the defense contractors, energy giants, banks, and "
                    "nation-states profiting from the US-Israel war on Iran.",
        category="investigation", subject="global-finance", featured=False,
        tags=["iran-war", "defense-contractors", "oil-and-gas",
              "military-industrial-complex", "blackrock"],
    ),
    "the-justice-departments-selective-incompetence.md": dict(
        title="The Justice Department's Selective Incompetence",
        description="The DOJ's failure to redact the names of Epstein's victims is not "
                    "a routine clerical lapse. It is a breakdown that now functions as "
                    "a barrier to further transparency.",
        category="analysis", subject="domestic-politics", featured=False,
        tags=["department-of-justice", "epstein-files", "transparency",
              "bureaucratic-corruption", "coverup"],
    ),
    "the-nuclear-pretense.md": dict(
        title="The Nuclear Pretense: What US Intelligence Actually Said",
        description="On the eve of war, US intelligence assessed that Iran was not "
                    "building a nuclear weapon and the IAEA found no structured "
                    "program. The strikes came anyway.",
        category="investigation", subject="world-affairs", featured=True,
        tags=["iran-war", "nuclear-weapons", "intelligence", "iaea",
              "preventive-war", "iraq-2003"],
    ),
    "the-peace-announcement-gap.md": dict(
        title="The Peace Announcement Gap: Why the US-Iran Deal Is Designed to Collapse",
        description="Trump declared a US-Iran peace deal complete an hour after Israel "
                    "bombed Beirut. The pattern isn't failed diplomacy—it is managed "
                    "instability serving a permanent war economy.",
        category="investigation", subject="world-affairs", featured=True,
        tags=["iran", "israel", "lebanon", "foreign-policy",
              "military-industrial-complex", "middle-east"],
    ),
    "the-phantom-menace-far-left-terrorism-framing.md": dict(
        title="The Phantom Menace: Inventing a Far-Left Terror Crisis",
        description="A data-driven look at the administration's new 'far-left "
                    "terrorism' push, the leaderless Antifa designation, and the "
                    "redirection of counterterror machinery toward political opponents.",
        category="investigation", subject="domestic-politics", featured=False,
        tags=["counterterrorism", "antifa", "civil-liberties", "dissent",
              "authoritarianism", "trump-administration"],
    ),
    "the-presidents-least-privilege-problem.md": dict(
        title="The Least-Privilege State: How Compartmentalized Programs Shape the World",
        description="From the Manhattan Project to the UAP disclosure fight, a look at "
                    "how Special Access Programs create a hidden layer of governance "
                    "with global consequences.",
        category="analysis", subject="surveillance-state", featured=False,
        tags=["special-access-programs", "classified-programs", "intelligence",
              "national-security", "oversight", "uap"],
    ),
    "the-two-party-system-and-the-convergence-of-power.md": dict(
        title="The Two-Party System and the Convergence of Power",
        description="A historical analysis of how two parties that perform rivalry "
                    "have converged on the policies that matter most to their donors.",
        category="analysis", subject="domestic-politics", featured=False,
        tags=["two-party-system", "political-history", "bipartisanship", "elites",
              "representation"],
    ),
    "the-uni-party-setup-authoritarianism-wasnt-a-glitch.md": dict(
        title="The Uni-Party Setup: Authoritarianism Wasn't a Glitch",
        description="The scoreboard never changes no matter who wins. What looks like "
                    "a partisan seesaw is a single power structure with two paint "
                    "colors—and an authoritarian turn built in.",
        category="essay", subject="domestic-politics", featured=False,
        tags=["uni-party", "authoritarianism", "big-tech", "elites",
              "trump-administration"],
    ),
    "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid.md": dict(
        title="Tragedy in Gaza: 62 Palestinians Killed, Many While Seeking Aid",
        description="Dozens of civilians desperate for food were killed at aid "
                    "distribution sites—the latest in a documented pattern of "
                    "violence against those seeking supplies.",
        category="briefing", subject="world-affairs", featured=False,
        tags=["gaza", "humanitarian-crises", "war-crimes", "aid-distribution"],
    ),
    "trump-untruth-tracker-second-term.md": dict(
        title="Trump Untruth Tracker: The Second-Term Ledger",
        description="A running account of Donald Trump's false and misleading public "
                    "statements from the 2024 campaign through his second presidency, "
                    "drawing on the major fact-checking desks.",
        category="briefing", subject="domestic-politics", featured=False,
        tags=["trump", "fact-check", "misinformation", "second-term", "media"],
    ),
    "trumps-crypto-empire-from-white-house-to-wallet.md": dict(
        title="Trump's Crypto Empire: From White House to Wallet",
        description="About 60% of Trump's reported net worth now comes from "
                    "cryptocurrency—a windfall that tracks uncomfortably well with "
                    "the policy he signs.",
        category="analysis", subject="domestic-politics", featured=False,
        tags=["trump", "cryptocurrency", "insider-trading", "conflicts-of-interest",
              "emoluments"],
    ),
    "un-mandate-partition-palestine.md": dict(
        title="From Balfour to Nakba: How Palestine Was Partitioned by Decree",
        description="A detailed look at the British Mandate, the UN partition vote, "
                    "and the violence that turned a Palestinian majority into a "
                    "dispossessed refugee population.",
        category="analysis", subject="history", featured=False,
        tags=["palestine", "nakba", "british-mandate", "united-nations",
              "colonialism", "zionism"],
    ),
    "world-commerce-corporation.md": dict(
        title="The World Commerce Corporation: OSS Veterans and the Postwar Shadow Market",
        description="A look at the World Commerce Corporation—its origins in the "
                    "British-American-Canadian Corporation, its intelligence-veteran "
                    "leadership, and the controversies that still surround it.",
        category="analysis", subject="history", featured=False,
        tags=["world-commerce-corporation", "oss", "william-donovan",
              "william-stephenson", "cold-war", "permindex"],
    ),
}

# Plain-text section labels to re-grade as `## ` headings (drawn from the
# headings the earlier fix-headers pass left unbolded).
PROMOTE = {
    "chinas-ai-sports-bots-a-cover-for-military-innovation.md": [],
    "israels-starvation-of-palestine-40000-babies-at-risk.md": [],
    "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid.md": [
        "Israel's War Crimes Continue",
        '"Tactical Pauses" Fail to Protect Civilians',
    ],
    "the-epstein-jail-video-pt-2-the-dojs-smoking-gun.md": [
        'The Official Story (Or, "Nothing to See Here")',
        'How "Conspiracy Theories" are Born',
        'The Mysterious "Orange Shape"',        "The Cursor and Menu That Shouldn't Exist",
        'The "Missing Minute"',
        "Staff Statements That Don't Match the Tape",
        'The Unmonitored Call to Epstein\'s "Mother"',
    ],
    "project-2025-the-conspiracy-that-isnt-a-theory.md": [
        "The Heritage Foundation's Origins",
        "The Courts Are the Last Firewall \u2014 And They're Under Siege",
        "What's Already Been Destroyed",
        "The 47% That Remains: What's Still on the Table",
    ],
    "the-two-party-system-and-the-convergence-of-power.md": [],
    "the-ai-misalignment-dilemna-the-need-for-global-regulations.md": [
        "Introduction: The Tech\u2011Bro Du\u202fJour",
        "Case Study 1: Large Language Models and Their Sneaky Misbehaviors",
        "Case Study 2: Reward Hacking in Game\u2011Playing Agents",
    ],
    "the-agentic-ai-era-and-the-new-geopolitical-order.md": [
        "Key Takeaways",
    ],
    "the-untruthed": [],
}

# Raw leading lines (exact, after strip) to delete — duplicate titles & decks.
DROP_LEADING = {
    "cia-origins.md": ["# How the CIA Was Born: From OSS to Cold War Shadow War"],
    "circles-in-the-grain-the-latest-global-crop-circle-season.md": [
        "# **CIRCLING THE UNKNOWN**",
        "## A Dispatch on the 2025 Global Crop Circle Season",
    ],
    "palantir-expanding-shadow.md": [
        "# Palantir: The Expanding Shadow of the Surveillance State",
    ],
    "the-global-financial-architecture-who-pulls-the-levers.md": [
        "# The Architecture of Global Finance: Who Holds the Levers",
    ],
    "the-integration-trap.md": ["# The Integration Trap"],
    "the-iran-war-profit-sheet.md": [
        "# The Iran War Profit Sheet",
        "## Who Makes Money When Missiles Fly",
    ],
    "the-nuclear-pretense.md": [
        "# The Nuclear Pretense",
        "## What US Intelligence Actually Said About Iran's Bomb",
    ],
    "the-peace-announcement-gap.md": [
        "# The Peace Announcement Gap",
        "## Why the US-Iran 'Deal' Is Designed to Collapse",
    ],
    "un-mandate-partition-palestine.md": [
        "# From Balfour to Nakba: How Palestine Was Stolen by Decree and by Force",
    ],
    "world-commerce-corporation.md": [
        "# The World Commerce Corporation: OSS, Intrepid, and the Postwar Shadow Market",
    ],
    "chatgpt-prompted-stand-up-comedian-hilarious.md": [
        '## Popular Specialized ChatGPT "Stand-Up Comedian"',
    ],
    "israels-starvation-of-palestine-40000-babies-at-risk.md": [
        "An Objective Glimpse into Israel's Recent War Crimes",
    ],
    "the-ai-misalignment-dilemna-the-need-for-global-regulations.md": [
        "## The AI Misalignment Dilemma & the Need for Global Regulations",
        "Based on \u201cCurrent Cases of AI Misalignment and Their Implications for "
        "Future Risks\u201d by Leonard Dung",
    ],
    "the-two-party-system-and-the-convergence-of-power.md": [
        "## A Historical Analysis of Political Co-operation",
    ],
    "the-justice-departments-selective-incompetence.md": [
        "## Why the DOJ\u2019s Redaction Failure Warrants Scrutiny, Not Just "
        "Apologies",
    ],
    "the-epstein-jail-video-pt-2-the-dojs-smoking-gun.md": [
        'How "Conspiracy Theories" are Born',
    ],
}

ROMAN = re.compile(r"^(?:[IVXLC]+|[0-9]+)\s*[\.\)]\s*", re.I)
ACRONYMS = {"AIPAC", "FDD", "IAI", "CIA", "FBI", "DOJ", "NDAA", "ICC", "ICE",
            "NSA", "UAP", "UFO", "AI", "BIS", "IMF", "CBSC", "MOU", "IRGC"}


def sentence_case(text: str) -> str:
    """ALL-CAPS heading -> sentence case, preserving leading acronyms."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        core = w.strip(".,:;()")
        if core in ACRONYMS:
            out.append(w)
        elif i == 0:
            out.append(w[:1].upper() + w[1:].lower())
        elif core in ACRONYMS:
            out.append(w)
        else:
            out.append(w.lower())
    return " ".join(out)


def clean_heading_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^\*+|\*+$", "", text).strip()
    text = ROMAN.sub("", text).strip()
    text = re.sub(r"^Part\s+[IVXLC0-9]+\s*[\.:\-—]\s*", "", text, flags=re.I)
    text = re.sub(r"\s*[\.\:]$", "", text).strip()
    if text and text.upper() == text and len(text.split()) > 1 and \
            text.strip("*").strip(".") not in ACRONYMS:
        text = sentence_case(text)
    return text


def split_frontmatter(raw: str):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", raw, re.S)
    return m.group(1), m.group(2)


def rewrite_frontmatter(meta: dict, old_pubdate) -> str:
    if hasattr(old_pubdate, "strftime"):
        pub = old_pubdate.strftime("%Y-%m-%d")
    else:
        pub = str(old_pubdate)[:10]
    lines = [
        "---",
        f'title: "{meta["title"]}"',
        f'description: "{meta["description"]}"',
        f"pubDate: {pub}",
        f'category: {meta["category"]}',
        f'subject: {meta["subject"]}',
        "tags:",
    ]
    lines += [f"  - {t}" for t in meta["tags"]]
    lines.append(f'featured: {str(meta["featured"]).lower()}')
    lines.append("---")
    return "\n".join(lines)


def promote_plain_labels(lines, labels):
    """Turn exact plain-text label lines into `## ` headings (if not already)."""
    wanted = {l.strip() for l in labels}
    out = []
    for ln in lines:
        s = ln.strip()
        if s in wanted:
            out.append("## " + s)
        else:
            out.append(ln)
    return out


def drop_leading(lines, drops):
    """Remove leading duplicate-title lines, skipping blanks."""
    remaining = list(lines)
    for d in drops:
        for i, ln in enumerate(remaining):
            if ln.strip() == d.strip():
                del remaining[i]
                break
    # collapse any blank lines left at the very top
    while remaining and not remaining[0].strip():
        remaining.pop(0)
    return remaining


def normalize_headings(lines):
    """Strip `**`, de-number, then lift levels so the first heading is `##`.

    Lines inside fenced code blocks are left untouched.
    """
    parsed, in_code = [], False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
            parsed.append(("t", 0, ln))
            continue
        m = None if in_code else re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            parsed.append(("h", len(m.group(1)), clean_heading_text(m.group(2))))
        else:
            parsed.append(("t", 0, ln))
    levels = [lvl for k, lvl, _ in parsed if k == "h"]
    if not levels:
        return lines
    shift = 2 - min(levels)  # first heading always becomes level 2
    out = []
    for k, lvl, txt in parsed:
        if k == "h":
            new_lvl = max(2, min(6, lvl + shift))
            out.append("#" * new_lvl + " " + txt)
        else:
            out.append(txt)
    return out


# Articles that carry no in-body sources block. Each entry is derived strictly
# from what that article itself names or draws on — never invented citations.
FALLBACK_SOURCES = {
    "chatgpt-creates-throne-portrait-my-digital-transformation.md":
        "*Image generated with ChatGPT (OpenAI). A personal note; no external "
        "reporting.*",
    "chatgpt-prompted-stand-up-comedian-hilarious.md":
        "*Set performed by a custom ChatGPT model found in the Sider AI "
        "catalogue. Satire.*",
    "circles-in-the-grain-the-latest-global-crop-circle-season.md":
        "*Crop-circle archives and media coverage of the 2025 season; published "
        "research on formation geometry and plant-node anomalies; farmer and "
        "researcher accounts.*",
    "human-beats-ai-in-10-hour-coding-marathon-heres-how.md":
        "*AtCoder World Tour Finals 2025; OpenAI's post-competition statement; "
        "competitive-programming records.*",
    "israeli-security-cabinets-decision-on-gaza.md":
        "*United Nations, World Health Organization, and European Commission "
        "statements; Israeli security and opposition statements; international "
        "press reporting.*",
    "project-2025-the-conspiracy-that-isnt-a-theory.md":
        "*Center for American Progress; Politico; Reuters; Axios; PBS NewsHour; "
        "Earthjustice; Government Executive; Human Rights Watch; JD Supra; the "
        "Varieties of Democracy (V-Dem) dataset; The Heritage Foundation's "
        "Mandate for Leadership.*",
    "the-integration-trap.md":
        "*FY2027 National Defense Authorization Act (Section 224); House Armed "
        "Services Committee markup (June 2026); International Criminal Court "
        "arrest warrants for Benjamin Netanyahu and Yoav Gallant (November "
        "2024); congressional and press reporting.*",
    "the-two-party-system-and-the-convergence-of-power.md":
        "*Historical record and federal voting records; press reporting on "
        "domestic military deployment and surveillance authorities.*",
    "the-uni-party-setup-authoritarianism-wasnt-a-glitch.md":
        "*Public statements, federal contracting records, and the historical "
        "record.*",
}

# --- Sources detection -----------------------------------------------------
# A sources *marker* opens the closing block. It may be a heading
# (`## Sources`, `## Sources & Reading`), a bold label
# (`**Sources and further reading:**`), or an inline italic paragraph
# (`*Sources: The Guardian, ...*`). Plain in-body `Sources:` notes are not the
# block — position decides — and they are italicized in place instead.
HEADING_SOURCES = re.compile(
    r"^sources(?:\s*(?:[&+]|and)\s*(?:further\s*)?reading)?$|"
    r"^(?:further|suggested)\s+reading$", re.I)
INLINE_SOURCES = re.compile(
    r"^(?:sources|further reading)\s*[:\u2014\-]\s*(.+)$", re.I)


def sources_marker(line):
    """Return (True, inline_text) when `line` opens a sources block."""
    s = line.strip()
    if not s:
        return (False, "")
    m = re.match(r"^#{2,4}\s+(.*)$", s)
    if m:
        inner = m.group(1).strip().strip("*").strip().rstrip(":").strip()
        return (bool(HEADING_SOURCES.match(inner)), "")
    m = re.match(r"^\*\*(.+?)\*\*\s*:?\s*$", s)
    if m and HEADING_SOURCES.match(m.group(1).strip().rstrip(":").strip()):
        return (True, "")
    core = s.strip("*").strip()
    m = INLINE_SOURCES.match(core)
    if m:
        return (True, m.group(1).rstrip("*").strip())
    return (False, "")


def italic_inline_sources(line):
    """Plain in-body `Sources: X` -> italic note so it is not read as a block."""
    s = line.strip()
    if s and not s.startswith("*") and INLINE_SOURCES.match(s):
        return "*" + s + "*"
    return line

# Inline noise left by the original paste: trailing signatures and bracketed
# citation keys such as [politico] / [americanprogress]+1 that render as
# literal junk. These are moved into (or already covered by) the sources block.
INLINE_SIG_RE = re.compile(r"\s*[-\u2014]{1,2}\s*(?:MiStyk|Mistyk|InsertaBot)\s*\.?\s*$")
CITE_TAG_RE = re.compile(r"\[([a-z][a-z0-9\.\-]{2,})\]\u200b?(?:\+\d+)?(?!\()")
REF_TAG_RE = re.compile(r"\s*\[ref:[^\]]*\]")
CITE_SUFFIX_RE = re.compile(r"(?<=[a-z\)\"\u201d])[a-z]{4,}\+[0-9]+(?=[\s\.\u2014]|$)")
BARE_URL_RE = re.compile(r"(?<![\(<\[`])https?://[^\s<>\)\]]+")
HASHTAG_LINE_RE = re.compile(r"^#([A-Za-z][^#]*)")
ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")


def strip_inline_noise(lines):
    """Remove paste artifacts that would render as literal junk in the body."""
    out = []
    for ln in lines:
        ln = ZERO_WIDTH_RE.sub("", ln)
        ln = CITE_TAG_RE.sub("", ln)
        ln = REF_TAG_RE.sub("", ln)
        ln = CITE_SUFFIX_RE.sub("", ln)
        ln = BARE_URL_RE.sub(lambda m: f"<{m.group(0)}>", ln)
        ln = re.sub(r"[ \t]+$", "", ln)
        if INLINE_SIG_RE.search(ln):
            ln = INLINE_SIG_RE.sub("", ln).rstrip()
            ln = re.sub(r"\s*[-\u2014]{1,2}\s*$", "", ln).rstrip()
        m = HASHTAG_LINE_RE.match(ln.strip())
        if m:
            ln = "- " + m.group(1).strip()
        out.append("" if not ln.strip() else ln)
    return out
CTA_RE = re.compile(
    r"independent publication|share it|continue the thread|consider sharing|"
    r"if you (enjoyed|found|liked)|engage in the thread", re.I)


def clean_source_text(t):
    t = t.strip().strip("*").strip()
    t = re.sub(r"^(?:Sources?|Further Reading)\s*[:\u2014\-]\s*", "", t, flags=re.I)
    return t.strip().strip("*").strip()


def normalize_sources(lines, name):
    """Rebuild the closing sources block as `---` + `## Sources` + entries.

    The block is the LAST sources-like marker, which must sit in the final
    stretch of the article (in-body `Sources:` notes never qualify).
    """
    n = len(lines)
    markers = []
    for i, l in enumerate(lines):
        ok, inline = sources_marker(l)
        if ok:
            markers.append((i, inline))

    idx, inline = None, ""
    for i, t in markers:
        if i >= 0.6 * n:
            idx, inline = i, t
    if idx is None:
        tail = [m for m in markers if m[0] >= n - 15]
        if tail:
            idx, inline = tail[-1]

    if idx is None:
        # No in-body sources: tidy the tail, then attach the per-article
        # fallback line (derived from what the piece itself references).
        out = tidy_tail(lines)
        fb = FALLBACK_SOURCES.get(name)
        if fb:
            out += ["", "---", "", "## Sources", "", fb]
        return out

    head = [italic_inline_sources(l) for l in lines[:idx]]

    collected = []
    txt = clean_source_text(inline)
    if txt:
        collected.append(f"*{txt}*")
    for ln in lines[idx + 1:]:
        s = ln.strip()
        if not s or s == "---":
            continue
        if sources_marker(s)[0]:
            continue
        if CTA_RE.search(s):
            continue
        if re.match(r"^[-*+]\s+", s):
            collected.append("- " + re.sub(r"^[-*+]\s+", "", s))
        else:
            t = clean_source_text(s)
            if t:
                collected.append(f"*{t}*")

    out = tidy_tail(head) + ["", "---", "", "## Sources", ""] + collected
    return out


SIG_RE = re.compile(r"^\s*[-—]{0,2}\s*(Mistyk|MiStyk|InsertaBot)\s*\.?\s*$")


def tidy_tail(lines):
    """Drop trailing rules, signatures, and inline-source tag noise."""
    out = list(lines)
    while out and not out[-1].strip():
        out.pop()
    while out and (out[-1].strip() == "---" or SIG_RE.match(out[-1])):
        out.pop()
        while out and not out[-1].strip():
            out.pop()
    # collapse 3+ blank lines
    cleaned, blanks = [], 0
    for ln in out:
        if not ln.strip():
            blanks += 1
            if blanks > 2:
                continue
        else:
            blanks = 0
        cleaned.append(ln)
    return cleaned


def bulletize_colon_runs(lines):
    """Turn orphan items into bullets after a lead-in line ending in ':'.

    The original pastes lost their `- ` markers, leaving bare lines after a
    colon lead-in. Fenced code blocks are skipped.
    """
    out = list(lines)
    run, in_code = False, False
    for i, ln in enumerate(out):
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            run = False
            continue
        if in_code:
            continue
        if not s:
            continue
        if s.startswith(("#", "|", ">", "*")):
            run = False
            continue
        if run and not s.startswith("-") and not re.match(r"^\d+[.)]\s", s):
            if s[-1] in ".?!\"\u201d)':;" and len(s) > 40:
                run = False
                continue
            if len(s) <= 200:
                out[i] = "- " + s
                continue
        if s.endswith(":") and len(s) < 240:
            run = True
        else:
            run = False
    return out


def fix_project_2025(lines):
    """Rebuild the 'Target / Goal' pair list as bullets before bulletizing."""
    out, i, n = [], 0, len(lines)
    while i < n:
        if lines[i].strip() == "Target":
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n and lines[j].strip() == "Goal":
                k, pending = j + 1, []
                while k < n:
                    t = lines[k].strip()
                    if not t:
                        k += 1
                        continue
                    if t.startswith("#"):
                        break
                    if t.endswith((".", "?", "!")) and len(t) > 60:
                        break
                    pending.append(t)
                    k += 1
                p = 0
                while p + 1 < len(pending):
                    out.append(f"- **{pending[p]}** \u2014 {pending[p + 1]}")
                    p += 2
                if p < len(pending):
                    out.append("- " + pending[p])
                out.append("")
                i = k
                continue
        out.append(lines[i])
        i += 1
    return out


def collapse_blank_runs(lines, max_blank=1):
    out, blanks, in_code = [], 0, False
    for ln in lines:
        if ln.strip().startswith("```"):
            in_code = not in_code
        if not ln.strip() and not in_code:
            blanks += 1
            if blanks > max_blank:
                continue
        else:
            blanks = 0
        out.append(ln)
    return out


def space_headings(lines):
    """Ensure exactly one blank line separates a heading from its neighbours."""
    out, in_code = [], False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            in_code = not in_code
            out.append(ln)
            continue
        is_h = (not in_code) and bool(re.match(r"^#{2,6}\s", ln))
        if not is_h:
            out.append(ln)
            continue
        if out and out[-1].strip():
            out.append("")
        out.append(ln)
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        # Insert a blank line before any following non-heading content,
        # INCLUDING a code fence, so headings never sit "tight" against
        # the next block. (A heading directly above a fence is valid
        # markdown, but strict uniformity wants the separating blank line.)
        if nxt.strip() and not re.match(r"^#{2,6}\s", nxt):
            out.append("")
    return out


FILE_FIXES = {
    "project-2025-the-conspiracy-that-isnt-a-theory.md": fix_project_2025,
}


def normalize_file(path):
    raw = open(path, encoding="utf-8").read()
    fm_text, body = split_frontmatter(raw)
    old = yaml.safe_load(fm_text)
    name = os.path.basename(path)
    meta = META[name]

    lines = body.split("\n")
    lines = strip_inline_noise(lines)
    lines = drop_leading(lines, DROP_LEADING.get(name, []))
    lines = promote_plain_labels(lines, PROMOTE.get(name, []))
    if name in FILE_FIXES:
        lines = FILE_FIXES[name](lines)
    lines = bulletize_colon_runs(lines)
    lines = normalize_headings(lines)
    lines = normalize_sources(lines, name)
    lines = space_headings(lines)
    lines = collapse_blank_runs(lines)

    new = rewrite_frontmatter(meta, old.get("pubDate")) + "\n\n" + \
        "\n".join(lines).strip() + "\n"
    open(path, "w", encoding="utf-8").write(new)
    return name


def main():
    files = sorted(glob.glob(os.path.join(D, "*.md")))
    missing = [os.path.basename(f) for f in files
               if os.path.basename(f) not in META]
    if missing:
        sys.exit("No META entry for: " + ", ".join(missing))
    for f in files:
        print("normalized:", normalize_file(f))
    print(f"\n{len(files)} dispatch files normalized.")


if __name__ == "__main__":
    main()
