from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1600, 990
bg_color = (18, 22, 20)
img = Image.new("RGB", (W, H), bg_color)
draw = ImageDraw.Draw(img)

# Subtle grid & background gradient accent
for y in range(H):
    r = int(16 + (y / H) * 8)
    g = int(22 + (y / H) * 12)
    b = int(18 + (y / H) * 10)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

for x in range(0, W, 40):
    draw.line([(x, 0), (x, H)], fill=(26, 34, 29), width=1)
for y in range(0, H, 40):
    draw.line([(0, y), (W, y)], fill=(26, 34, 29), width=1)

def get_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_mono_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/courbd.ttf" if bold else "C:/Windows/Fonts/cour.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return get_font(size, bold)

f_title = get_font(30, True)
f_sub = get_font(16, False)
f_sub_b = get_font(16, True)
f_kpi_lbl = get_font(13, True)
f_kpi_val = get_font(23, True)
f_kpi_sub = get_font(13, False)
f_col_hdr = get_font(19, True)
f_sec_hdr = get_font(15, True)
f_body = get_font(13, False)
f_body_b = get_font(13, True)
f_small = get_font(12, False)
f_small_b = get_font(12, True)
f_mono = get_mono_font(13, True)

c_card = (27, 33, 29)
c_card_alt = (32, 40, 35)
c_border = (68, 92, 74)
c_gold = (238, 190, 84)
c_green = (108, 212, 130)
c_blue = (106, 184, 238)
c_amber = (242, 158, 76)
c_cream = (237, 224, 212)
c_white = (245, 248, 246)
c_muted = (170, 184, 174)

# Header bar
draw.rounded_rectangle([24, 20, W - 24, 118], radius=14, fill=(24, 32, 27), outline=c_border, width=2)

# Paste official Kintara logo (kins-logo.png)
logo_path = os.path.join(os.path.dirname(__file__), "kins-logo.png")
if os.path.exists(logo_path):
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((72, 72), Image.Resampling.LANCZOS)
    img.paste(logo, (42, 33), logo)
    draw.ellipse([40, 31, 116, 107], outline=c_gold, width=2)

draw.text((132, 29), "KINTARA ($KINS) — ON-CHAIN ECONOMY, UTILITY & PRODUCT ANALYSIS", font=f_title, fill=c_cream)
draw.text((132, 66), "Browser & Solana Mobile Isometric MMO  •  Mycelium Strategy Partner (#5 Allocation: $2,730.47 USD / 8.77% in Raydium MYC/KINS)", font=f_sub_b, fill=c_green)
draw.text((132, 90), "Solana Mint (CA): Tqj8yFmagrg7oorpQkVGYR52r96RFTamvWfth9bpump   |   Website: kintara.com   |   Docs: kintara.com/#docs   |   X: @PlayKintara", font=f_mono, fill=c_muted)

# Right badge in header
draw.rounded_rectangle([W - 310, 34, W - 42, 104], radius=10, fill=(36, 52, 40), outline=c_green, width=2)
draw.text((W - 292, 43), "VERIFIED SNAPSHOT", font=f_kpi_lbl, fill=c_gold)
draw.text((W - 292, 62), "2026-10-25 UTC", font=f_col_hdr, fill=c_white)
draw.text((W - 292, 84), "Independent Research (Not Official)", font=f_small, fill=c_muted)

# KPI Row (6 cards)
kpis = [
    ("MARKET CAP / FDV", "$315,205 USD", "Price: $0.0003178 (DexScreener)", c_gold),
    ("PRIMARY DEX LIQUIDITY", "$91,308.84 USD", "PumpSwap KINS/SOL ($97.18K Total)", c_green),
    ("24H TRADING VOLUME", "$30,086.89 USD", "733 Txns (324 Buys / 409 Sells)", c_blue),
    ("CIRCULATING / BURNED", "991.69M $KINS", "8,307,029 KINS (0.83%) Burned", c_amber),
    ("MYCELIUM STRATEGY LP", "$2,730.47 USD", "8.77% Share (#5 of 10 Projects)", c_green),
    ("LIVE GAME TELEMETRY", "456 Online Now", "69,546 Registered Accounts", c_blue),
]

kpi_w = (W - 48 - 5 * 14) // 6
kpi_y = 132
kpi_h = 92
for i, (lbl, val, sub, col) in enumerate(kpis):
    kx = 24 + i * (kpi_w + 14)
    draw.rounded_rectangle([kx, kpi_y, kx + kpi_w, kpi_y + kpi_h], radius=10, fill=c_card, outline=c_border, width=1)
    draw.rectangle([kx, kpi_y + 10, kx + 4, kpi_y + kpi_h - 10], fill=col)
    draw.text((kx + 16, kpi_y + 11), lbl, font=f_kpi_lbl, fill=c_muted)
    draw.text((kx + 16, kpi_y + 32), val, font=f_kpi_val, fill=col)
    draw.text((kx + 16, kpi_y + 64), sub, font=f_kpi_sub, fill=c_white)

# 3 Main Columns
col_y = 238
col_h = 694
col_w = (W - 48 - 2 * 18) // 3

# --- COLUMN 1: WHAT IS LIVE TODAY VS. PLANNED ---
c1x = 24
draw.rounded_rectangle([c1x, col_y, c1x + col_w, col_y + col_h], radius=12, fill=c_card, outline=c_border, width=2)
draw.rounded_rectangle([c1x, col_y, c1x + col_w, col_y + 44], radius=12, fill=(35, 58, 43), outline=c_border, width=1)
draw.text((c1x + 18, col_y + 11), "1. WHAT IS LIVE TODAY (v6.0) VS. PLANNED", font=f_col_hdr, fill=c_cream)

cy = col_y + 56
draw.text((c1x + 18, cy), "LIVE TODAY — 36 PUBLIC UPDATES SHIPPED (MAY–SEPT 2026)", font=f_sec_hdr, fill=c_green)
cy += 24
live_items = [
    ("Free-to-Play Onboarding (v5.9):", "Free up to Total Level 10 across 5 core realms (Mainland, Wilderness, Whisperwood, Frostmere, The Pond)."),
    ("Frictionless Login & Mobile:", "Non-custodial Privy login (Email, Google, Discord, X, Passkey) + Solana Mobile Wallet Adapter (Seeker app)."),
    ("6 Skills & 10+ Connected Realms:", "Combat, Woodcutting, Mining, Fishing, Cooking & Smithing (Level 40 cap) + Server 1 & 2 (EU/Asia regional fleets)."),
    ("v6.0 Relicweaver & The Deep:", "Qadim in The Dunes binds 60 permanent Relics (5 gold/roll, up to 10 rerolls); raft-only 5th fishing zone The Deep."),
    ("v6.0 Minigames & Casino Floor:", "Wagered Kintara FPS & Falling Tiles + 5 provably-fair v2 casino games (Crash, Plinko, Keno, Slots; 96% RTP)."),
    ("Social Rooms & Seasons:", "Kintara Navigator rentable player rooms, Season 1 reward pass, Collection Log, and monthly Guild Seasons."),
]
for title_b, desc_t in live_items:
    draw.ellipse([c1x + 20, cy + 5, c1x + 28, cy + 13], fill=c_green)
    draw.text((c1x + 34, cy), title_b, font=f_body_b, fill=c_white)
    cy += 18
    words = desc_t.split(" ")
    line = ""
    for w in words:
        if len(line + " " + w) <= 68:
            line = (line + " " + w).strip()
        else:
            draw.text((c1x + 34, cy), line, font=f_body, fill=c_muted)
            cy += 17
            line = w
    if line:
        draw.text((c1x + 34, cy), line, font=f_body, fill=c_muted)
        cy += 21

cy += 4
draw.line([(c1x + 18, cy), (c1x + col_w - 18, cy)], fill=c_border, width=1)
cy += 12
draw.text((c1x + 18, cy), "PLANNED FEATURES & ROADMAP TRANSPARENCY", font=f_sec_hdr, fill=c_amber)
cy += 24
planned_items = [
    ("No Formal Roadmap Published:", "Kintara publishes live patch notes (/news) rather than a multi-quarter roadmap or speculative whitepaper."),
    ("Documented Planned Systems:", "Official Game Guide (#docs) flags Parties & Teleport-to-Friend, general PvE mob loot drops, expanded cooking recipes, and Club camera keybind remapping (V/P) for future updates."),
    ("Key Risk & Open Question:", "5+ week cadence gap since v6.0 (2026-09-14) + custodial and regulatory surface of in-game $KINS wagering & 96%-RTP casino games."),
]
for title_b, desc_t in planned_items:
    draw.ellipse([c1x + 20, cy + 5, c1x + 28, cy + 13], fill=c_amber)
    draw.text((c1x + 34, cy), title_b, font=f_body_b, fill=c_cream)
    cy += 18
    words = desc_t.split(" ")
    line = ""
    for w in words:
        if len(line + " " + w) <= 68:
            line = (line + " " + w).strip()
        else:
            draw.text((c1x + 34, cy), line, font=f_body, fill=c_muted)
            cy += 17
            line = w
    if line:
        draw.text((c1x + 34, cy), line, font=f_body, fill=c_muted)
        cy += 21

# --- COLUMN 2: $KINS TOKENOMICS, ACCESS GATE & SINKS ---
c2x = c1x + col_w + 18
draw.rounded_rectangle([c2x, col_y, c2x + col_w, col_y + col_h], radius=12, fill=c_card, outline=c_border, width=2)
draw.rounded_rectangle([c2x, col_y, c2x + col_w, col_y + 44], radius=12, fill=(48, 52, 30), outline=c_border, width=1)
draw.text((c2x + 18, col_y + 11), "2. $KINS TOKEN UTILITY & DEFLATIONARY SINKS", font=f_col_hdr, fill=c_gold)

cy = col_y + 56
draw.text((c2x + 18, cy), "TWO-STAGE 1,000 $KINS (~$0.32 USD) ACCESS GATE", font=f_sec_hdr, fill=c_gold)
cy += 24

gate_cards = [
    ("STAGE 1: HOLD 1,000 $KINS (INSTANT UNLOCK)", "Lifts Total Level 10 cap; opens paid biomes (The Shores, The Dunes, The Emberstone, The Venomweaver) and activates rare mount & pet drops.", c_green),
    ("STAGE 2: HOLD 1,000 $KINS FOR 24 HOURS (VALUE-OUT)", "Unlocks Marketplace selling, P2P player trades, PvP & minigame wagers, guild-bank deposits, and Wilderness tombstone recovery.", c_blue),
]
for g_title, g_desc, g_col in gate_cards:
    draw.rounded_rectangle([c2x + 18, cy, c2x + col_w - 18, cy + 84], radius=8, fill=c_card_alt, outline=g_col, width=1)
    draw.text((c2x + 28, cy + 8), g_title, font=f_body_b, fill=g_col)
    words = g_desc.split(" ")
    line = ""
    ly = cy + 28
    for w in words:
        if len(line + " " + w) <= 66:
            line = (line + " " + w).strip()
        else:
            draw.text((c2x + 28, ly), line, font=f_body, fill=c_white)
            ly += 17
            line = w
    if line:
        draw.text((c2x + 28, ly), line, font=f_body, fill=c_white)
    cy += 94

cy += 6
draw.text((c2x + 18, cy), "DOCUMENTED ON-CHAIN $KINS SINKS & REVENUE FLOWS", font=f_sec_hdr, fill=c_green)
cy += 26

sink_cards = [
    ("Paid Spinner Wheel ($5 USD in $KINS / Spin)", [
        "• 50% Permanently Burned on Solana + 50% to Game Treasury",
        "• 1 Free Spin every 24h (requires Avg Skill Level 5; 22 segments)",
        "• Verified On-Chain Burn: 8,307,029.22 $KINS (0.83% of 1B supply)"
    ], c_amber),
    ("Player Marketplace (Gold-for-$KINS & Gear)", [
        "• 95% Paid to Seller + 5% to Game Treasury in 1 atomic tx",
        "• Referral rewards paid in $KINS inside the buyer's transaction",
        "• Supports Relic-filtered gear markets & USD-quoted gold listings"
    ], c_green),
    ("In-Game $KINS Custody Layer (Update v6.0)", [
        "• Deposit $KINS for instant Minigames hub wagering (FPS / Tiles)",
        "• Deposited balance still counts toward 1,000 $KINS hold gate",
        "• Automatic on-chain withdrawals with a 1% protocol fee"
    ], c_blue),
]

for s_title, s_lines, s_col in sink_cards:
    draw.rounded_rectangle([c2x + 18, cy, c2x + col_w - 18, cy + 102], radius=8, fill=c_card_alt, outline=c_border, width=1)
    draw.rectangle([c2x + 18, cy + 8, c2x + 22, cy + 94], fill=s_col)
    draw.text((c2x + 30, cy + 8), s_title, font=f_body_b, fill=s_col)
    sy = cy + 30
    for sl in s_lines:
        draw.text((c2x + 30, sy), sl, font=f_body, fill=c_white)
        sy += 21
    cy += 112

# --- COLUMN 3: HOLDER TIER LADDER, SECURITY & MYCELIUM ---
c3x = c2x + col_w + 18
draw.rounded_rectangle([c3x, col_y, c3x + col_w, col_y + col_h], radius=12, fill=c_card, outline=c_border, width=2)
draw.rounded_rectangle([c3x, col_y, c3x + col_w, col_y + 44], radius=12, fill=(32, 48, 56), outline=c_border, width=1)
draw.text((c3x + 18, col_y + 11), "3. HOLDER TIERS, SECURITY & MYCELIUM LP", font=f_col_hdr, fill=c_blue)

cy = col_y + 56
draw.text((c3x + 18, cy), "$KINS HOLDER XP LADDER & 24H THRESHOLD PERKS (v5.8)", font=f_sec_hdr, fill=c_gold)
cy += 24

tiers = [
    ("White (1,000+ KINS)", "Base Access", "Paid Realms + Value-Out (24h)"),
    ("Blue (10,000+ KINS)", "+1% XP", "25K: 2x Daily Quest XP"),
    ("Green (100,000+ KINS)", "+2% XP", "50K: 30 Inv Slots + 5 Outfits"),
    ("Gold (1,000,000+ KINS)", "+3% XP", "75K: +48 Bank Slots + 2nd Spin"),
    ("Purple (5,000,000+ KINS)", "+4% (+9% Guild)", "100K: +5 Market Listings"),
]

# Table header
draw.rounded_rectangle([c3x + 18, cy, c3x + col_w - 18, cy + 28], radius=6, fill=(42, 54, 48))
draw.text((c3x + 24, cy + 6), "Tier / Balance", font=f_small_b, fill=c_gold)
draw.text((c3x + 186, cy + 6), "XP Boost", font=f_small_b, fill=c_gold)
draw.text((c3x + 292, cy + 6), "24h Threshold Perks", font=f_small_b, fill=c_gold)
cy += 32

for t_name, t_xp, t_perk in tiers:
    draw.rounded_rectangle([c3x + 18, cy, c3x + col_w - 18, cy + 28], radius=4, fill=c_card_alt)
    draw.text((c3x + 24, cy + 6), t_name, font=f_small, fill=c_white)
    draw.text((c3x + 186, cy + 6), t_xp, font=f_small_b, fill=c_green)
    draw.text((c3x + 292, cy + 6), t_perk, font=f_small, fill=c_cream)
    cy += 32

cy += 10
draw.line([(c3x + 18, cy), (c3x + col_w - 18, cy)], fill=c_border, width=1)
cy += 12
draw.text((c3x + 18, cy), "ON-CHAIN DISTRIBUTION & SECURITY AUDIT (2026-10-25)", font=f_sec_hdr, fill=c_green)
cy += 24

sec_rows = [
    ("Token Program & Auth:", "Token-2022 | Mint & Freeze: Revoked (null)"),
    ("Supply (Slot 461,180,340):", "991,692,970.78 KINS (6 Decimals)"),
    ("Top 10 Non-LP Holders:", "18.54% Combined (Max Single Wallet: 3.00%)"),
    ("Primary Pool (PumpSwap):", "$91,308.84 USD (14.68% of Supply in LP)"),
    ("Other DEX Pools (Solana):", "$3,073.93 Meteora DLMM + $55.13 Orca WP"),
]
for k_lbl, k_val in sec_rows:
    draw.text((c3x + 20, cy), k_lbl, font=f_body_b, fill=c_muted)
    draw.text((c3x + 205, cy), k_val, font=f_body, fill=c_white)
    cy += 23

cy += 8
draw.line([(c3x + 18, cy), (c3x + col_w - 18, cy)], fill=c_border, width=1)
cy += 12
draw.text((c3x + 18, cy), "MYCELIUM STRATEGY CONNECTION ($MYC / $KINS)", font=f_sec_hdr, fill=c_gold)
cy += 24

draw.rounded_rectangle([c3x + 18, cy, c3x + col_w - 18, col_y + col_h - 16], radius=8, fill=(35, 46, 36), outline=c_gold, width=1)
myc_lines = [
    "• Active in Mycelium Strategy (myceliumfinance.com/allocations)",
    "• Raydium Pool: FmyAWpcEGTrV7hHdZ391kKycektEBZzoetL6GtjDkLua",
    "• Planted Liquidity: $2,730.47 USD (8.77% of $31,136.61 Total)",
    "• Ranks #5 of 10 Partner Allocations (4.39M KINS + 65.72M MYC)",
    "• Community: discord.gg/5M7FsQcGq  |  @myceliumfinance"
]
my_y = cy + 12
for ml in myc_lines:
    draw.text((c3x + 26, my_y), ml, font=f_body, fill=c_cream)
    my_y += 23

# Footer bar
draw.rounded_rectangle([24, H - 46, W - 24, H - 12], radius=8, fill=(22, 28, 24), outline=c_border, width=1)
footer_text = "AI-created for a Mycelium Finance bounty  •  Independent Analysis Infographic (Not an official Kintara announcement)  •  Data observed: 2026-10-25 UTC (DexScreener, Solana RPC, RugCheck, kintara.com, myceliumfinance.com)"
draw.text((40, H - 36), footer_text, font=f_small, fill=c_muted)

out_path = os.path.join(os.path.dirname(__file__), "kintara-kins-analysis.png")
img.save(out_path, "PNG", optimize=True)
print("Saved:", out_path, os.path.getsize(out_path))
