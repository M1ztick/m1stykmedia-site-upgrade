import re, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(BASE, "src/content/dispatch")

files_sections = {
    "human-beats-ai-in-10-hour-coding-marathon-heres-how.md": [
        "The Showdown in Tokyo",
        "The Final Score",
        "The How and Why?",
        "Looking Ahead",
        "Who Is \u201cPsyho\u201d?",
        "The Bigger Picture",
    ],
    "israeli-security-cabinets-decision-on-gaza.md": [
        "Escalation Without Clear Planning",
        "A Risky Escalation",
        "Lack of Planning and Unintended Consequences",
        "Humanitarian Crisis Deepens",
        "Final Thoughts",
    ],
    "israels-starvation-of-palestine-40000-babies-at-risk.md": [
        "An Objective Glimpse into Israel\u2019s Recent War Crimes",
        "A Personal Reflection",
    ],
    "the-two-party-system-and-the-convergence-of-power.md": [
        "A Historical Analysis of Political Co-operation",
        "Introduction",
        "The Origins: From No Parties to Two",
        "The Historical Timeline (1776 \u2192 Today)",
        "Bipartisan Policies: The Great Convergence",
        "Final Thoughts: The House Always Wins",
    ],
    "the-uni-party-setup-authoritarianism-wasnt-a-glitch.md": [
        "Introduction",
        "From Reagan to Biden: Different Names, Same Winners",
        "My Biden Setup Theory",
        "Why the Strongman Suits the Moment",
        "The Big Tech Twist",
        "The Uni-Party\u2019s Long Game",
        "Call It What It Is",
    ],
    "trumps-crypto-empire-from-white-house-to-wallet.md": [
        "Trump\u2019s Crypto Empire",
        "From White House to Wallet",
        "Trump\u2019s $TRUMP Meme Coin",
        "Insider Trading Shenanigans: Tariffs, Tweets, and Timely Trades Now",
        "Beyond Crypto",
        "The Ethical Tightrope",
        "Innovation vs. Opportunism",
    ],
    "tragedy-in-gaza-israeli-forces-kill-62-palestinians-many-while-seeking-aid.md": [
        "Israel\u2019s War Crimes Continue",
        "\u201cTactical Pauses\u201d Fail to Protect Civilians",
        "Growing International Concerns",
        "A Deepening Humanitarian Catastrophe",
    ],
    "the-epstein-jail-video-pt-2-the-dojs-smoking-gun.md": [
        "The Official Story (Or, \u201cNothing to See Here\u201d)",
        "How \u201cConspiracy Theories\u201d are Born",
        "Wrong Angles, Wrong Assumptions",
        "The Mysterious \u201cOrange Shape\u201d",
        "The Cursor and Menu That Shouldn\u2019t Exist",
        "The \u201cMissing Minute\u201d",
        "Staff Statements That Don\u2019t Match the Tape",
        "The Unmonitored Call to Epstein\u2019s \u201cMother\u201d",
        "The Inmates and the Silence",
        "Expert Criticism and Shrugging Bureaucrats",
        "Final Thoughts",
    ],
    "the-justice-departments-selective-incompetence.md": [
        "Why the DOJ\u2019s Redaction Failure Warrants Scrutiny, Not Just Apologies",
    ],
    "the-agentic-ai-era-and-the-new-geopolitical-order.md": [
        "Abstract",
        "1. The Technological Pivot: The Rise of Agentic and Multimodal Systems",
        "2. The Geopolitical Chessboard: Hegemony vs. Asymmetry",
        "3. Implications for the Next Decade (2025\u20132035)",
    ],
    "the-ai-misalignment-dilemna-the-need-for-global-regulations.md": [
        "The AI Misalignment Dilemma & the Need for Global Regulations",
        "Introduction: The Tech\u2011Bro DuJour",
        "The Ticking AI Time Bomb",
        "What Exactly Is AI Misalignment? A Deep Dive",
        "Case Study1: Large Language Models (Like ChatGPT) and Their Sneaky Misbehaviors",
        "Case Study2: Reward Hacking in Game\u2011Playing Agents",
        "Key Features of Misalignment: Why It\u2019s So Damn Tricky",
        "Legal Responsibilities of U.S.\u2013Based Tech Companies: A Bare Minimum That\u2019s Falling Short",
        "The Call for Global Regulations: Time to Step Up",
    ],
    "project-2025-the-conspiracy-that-isnt-a-theory.md": [
        "Introduction To Project 2025",
        "The Heritage Foundation\u2019s Origins",
        "A Power Grab, Not a Policy Plan",
        "The Civil Service Purge Is Already Happening",
        "The Courts Are the Last Firewall \u2014 And They\u2019re Under Siege",
        "What\u2019s Already Been Destroyed",
        "The 47% That Remains: What\u2019s Still on the Table",
        "Resistance Is Not Optional",
    ],
}

for filename, sections in files_sections.items():
    path = os.path.join(D, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for section in sections:
        content = re.sub(r"(?m)^(" + re.escape(section) + r")$", r"## \1", content)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("done:", filename)
