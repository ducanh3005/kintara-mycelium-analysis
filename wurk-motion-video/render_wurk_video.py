#!/usr/bin/env python3
"""
WURK Programmatic Product & Motion Graphics Video Generator
===========================================================
Renders a 24-second, 1920x1080 (Full HD @ 30fps) MP4 motion graphics video
with synthesized stereo ambient audio showcasing how AI agents and humans
work together on WURK (https://wurk.fun).

Requirements:
  pip install pillow numpy imageio-ffmpeg

Usage:
  python render_wurk_video.py
"""

import os
import math
import wave
import struct
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 24.0
TOTAL_FRAMES = int(FPS * DURATION)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "wurk-logo.jpg")
AUDIO_PATH = os.path.join(BASE_DIR, "wurk-audio.wav")
OUTPUT_MP4 = os.path.join(BASE_DIR, "wurk-product-motion-video.mp4")


def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - pow(1.0 - t, 3)


def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def load_font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def load_mono_font(size: int):
    candidates = [
        "C:/Windows/Fonts/consolab.ttf",
        "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/courbd.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return load_font(size, bold=True)


FONTS = {
    "hero": load_font(74, bold=True),
    "h1": load_font(58, bold=True),
    "h2": load_font(38, bold=True),
    "h3": load_font(30, bold=True),
    "body": load_font(26, bold=False),
    "body_bold": load_font(26, bold=True),
    "small": load_font(21, bold=False),
    "mono": load_mono_font(25),
    "mono_lg": load_mono_font(44),
    "cta": load_font(64, bold=True),
}


def prepare_logo_assets(logo_path: str):
    """Loads wurk-logo.jpg and extracts a clean RGBA alpha mask + badge variants."""
    raw = Image.open(logo_path).convert("L")
    arr = np.array(raw, dtype=np.float32)
    # Black glyph on white background -> invert for alpha
    alpha = np.clip((250.0 - arr) * 1.4, 0, 255).astype(np.uint8)
    alpha_img = Image.fromarray(alpha, mode="L")

    # White glyph on transparent background
    white_logo = Image.new("RGBA", raw.size, (255, 255, 255, 0))
    white_logo.putalpha(alpha_img)

    # Mint/Cyan gradient glyph on transparent background
    w, h = raw.size
    grad = np.zeros((h, w, 4), dtype=np.uint8)
    for y in range(h):
        ratio = y / max(1, h - 1)
        r = int(16 * (1 - ratio) + 0 * ratio)
        g = int(245 * (1 - ratio) + 210 * ratio)
        b = int(160 * (1 - ratio) + 255 * ratio)
        grad[y, :, 0] = r
        grad[y, :, 1] = g
        grad[y, :, 2] = b
    grad[:, :, 3] = alpha
    neon_logo = Image.fromarray(grad, mode="RGBA")

    # Rounded white card badge with original black WURK logo
    badge_size = 240
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(badge)
    bdraw.rounded_rectangle(
        [0, 0, badge_size - 1, badge_size - 1],
        radius=48,
        fill=(255, 255, 255, 255),
        outline=(16, 245, 160, 255),
        width=4,
    )
    inner = raw.resize((176, 176), Image.Resampling.LANCZOS).convert("RGBA")
    badge.paste(inner, (32, 32))

    return {
        "white": white_logo,
        "neon": neon_logo,
        "badge": badge,
    }


def generate_audio(output_wav: str, duration: float = DURATION):
    """Synthesizes a warm, futuristic stereo ambient soundtrack with scene chimes."""
    sample_rate = 44100
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # Warm Cmaj9 ambient pad (C3, G3, B3, D4, E4)
    freqs = [130.81, 196.00, 246.94, 293.66, 329.63]
    left = np.zeros_like(t)
    right = np.zeros_like(t)
    for idx, f in enumerate(freqs):
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * (0.18 + 0.05 * idx) * t + idx)
        wave_l = np.sin(2 * np.pi * f * t) * lfo
        wave_r = np.sin(2 * np.pi * (f * 1.002) * t + 0.4 * idx) * lfo
        weight = 0.12 / (1 + idx * 0.2)
        left += weight * wave_l
        right += weight * wave_r

    # Subtle rhythmic pulse at 110 BPM
    beat_env = 0.5 + 0.5 * np.sin(2 * np.pi * (110.0 / 60.0) * t)
    bass = 0.08 * np.sin(2 * np.pi * 65.41 * t) * (beat_env ** 2)
    left += bass
    right += bass

    # Scene transition crystalline chimes at 0.1s, 4.5s, 9.5s, 14.5s, 19.5s
    chime_times = [0.1, 4.5, 9.5, 14.5, 19.5]
    chime_notes = [523.25, 659.25, 783.99, 1046.50]
    for ct in chime_times:
        for n_idx, nf in enumerate(chime_notes):
            start_t = ct + n_idx * 0.07
            mask = t >= start_t
            dt = np.zeros_like(t)
            dt[mask] = t[mask] - start_t
            env = np.zeros_like(t)
            env[mask] = np.exp(-4.5 * dt[mask]) * (1 - np.exp(-80 * dt[mask]))
            tone = 0.06 * np.sin(2 * np.pi * nf * dt) * env
            left += tone * (0.8 if n_idx % 2 == 0 else 0.5)
            right += tone * (0.5 if n_idx % 2 == 0 else 0.8)

    # Master fade-in (0.8s) and fade-out (1.5s)
    fade_in = np.clip(t / 0.8, 0.0, 1.0)
    fade_out = np.clip((duration - t) / 1.5, 0.0, 1.0)
    master = fade_in * fade_out

    left = np.clip(left * master, -0.95, 0.95)
    right = np.clip(right * master, -0.95, 0.95)

    stereo = np.empty((total_samples * 2,), dtype=np.int16)
    stereo[0::2] = (left * 32767).astype(np.int16)
    stereo[1::2] = (right * 32767).astype(np.int16)

    with wave.open(output_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(stereo.tobytes())


def draw_background(frame_idx: int, logos: dict) -> Image.Image:
    """Draws the animated dark cyber-grid background and header bar."""
    t = frame_idx / FPS
    img = Image.new("RGBA", (WIDTH, HEIGHT), (8, 12, 22, 255))
    draw = ImageDraw.Draw(img)

    # Subtle animated grid lines
    offset_x = int((t * 35) % 80)
    offset_y = int((t * 20) % 80)
    grid_color = (22, 33, 56, 255)
    for x in range(-80 + offset_x, WIDTH + 80, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=grid_color, width=1)
    for y in range(-80 + offset_y, HEIGHT + 80, 80):
        draw.line([(0, y), (WIDTH, y)], fill=grid_color, width=1)

    # Top persistent navigation bar
    draw.rectangle([0, 0, WIDTH, 86], fill=(10, 16, 30, 235))
    draw.line([(0, 86), (WIDTH, 86)], fill=(16, 245, 160, 110), width=2)

    # Corner WURK badge + brand title in header
    small_badge = logos["badge"].resize((54, 54), Image.Resampling.LANCZOS)
    img.paste(small_badge, (48, 16), small_badge)
    draw.text((118, 22), "WURK", font=FONTS["h2"], fill=(255, 255, 255, 255))
    draw.text(
        (255, 30),
        "•  HUMAN + AGENT LABOR PROTOCOL",
        font=FONTS["small"],
        fill=(16, 245, 160, 255),
    )

    # Right header pill
    draw.rounded_rectangle(
        [WIDTH - 310, 20, WIDTH - 48, 68],
        radius=24,
        fill=(18, 32, 54, 255),
        outline=(0, 210, 255, 180),
        width=2,
    )
    draw.text(
        (WIDTH - 282, 31),
        "https://wurk.fun",
        font=FONTS["mono"],
        fill=(0, 230, 255, 255),
    )

    # Bottom progress timeline indicator
    prog_w = int((frame_idx / max(1, TOTAL_FRAMES - 1)) * WIDTH)
    draw.rectangle([0, HEIGHT - 8, WIDTH, HEIGHT], fill=(20, 30, 50, 255))
    draw.rectangle([0, HEIGHT - 8, prog_w, HEIGHT], fill=(16, 245, 160, 255))

    return img


def draw_centered_text(draw, y: int, text: str, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, y), text, font=font, fill=fill)


def render_scene_1(img: Image.Image, local_t: float, logos: dict):
    """Scene 1 (0.0s - 4.5s): Brand Hook — Agents & Humans Working Together."""
    draw = ImageDraw.Draw(img)
    enter = ease_out_cubic(local_t / 0.9)

    # Central WURK Logo Badge with animated pulse ring
    pulse = 1.0 + 0.04 * math.sin(local_t * 4.5)
    logo_size = int(210 * enter * pulse)
    if logo_size > 20:
        cx, cy = WIDTH // 2, 340
        ring_r = int(145 * enter + 12 * math.sin(local_t * 3.0))
        draw.ellipse(
            [cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r],
            outline=(16, 245, 160, 160),
            width=4,
        )
        badge = logos["badge"].resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        img.paste(badge, (cx - logo_size // 2, cy - logo_size // 2), badge)

    # Left Node: AI AGENTS
    left_x = int(-300 + 580 * ease_out_cubic((local_t - 0.2) / 0.9))
    draw.rounded_rectangle(
        [left_x - 210, 265, left_x + 210, 415],
        radius=28,
        fill=(14, 28, 52, 245),
        outline=(0, 210, 255, 255),
        width=3,
    )
    draw.text((left_x - 165, 290), "AUTONOMOUS AGENTS", font=FONTS["h3"], fill=(0, 225, 255, 255))
    draw.text((left_x - 165, 340), "24/7 API Execution • Code • Data", font=FONTS["small"], fill=(200, 220, 245, 255))
    draw.text((left_x - 165, 372), "SIWX Wallet Auth • Instant Bid", font=FONTS["small"], fill=(130, 175, 220, 255))

    # Right Node: HUMANS
    right_x = int(WIDTH + 300 - 580 * ease_out_cubic((local_t - 0.2) / 0.9))
    draw.rounded_rectangle(
        [right_x - 210, 265, right_x + 210, 415],
        radius=28,
        fill=(14, 36, 38, 245),
        outline=(16, 245, 160, 255),
        width=3,
    )
    draw.text((right_x - 165, 290), "HUMAN WURKERS", font=FONTS["h3"], fill=(16, 245, 160, 255))
    draw.text((right_x - 165, 340), "Creative Direction • Real World", font=FONTS["small"], fill=(200, 240, 225, 255))
    draw.text((right_x - 165, 372), "High-Judgment Verification", font=FONTS["small"], fill=(140, 210, 180, 255))

    # Animated energy packets between Left <-> Center <-> Right
    if local_t > 0.7:
        for i in range(4):
            phase = (local_t * 0.9 + i * 0.25) % 1.0
            px1 = int((left_x + 210) + phase * (WIDTH // 2 - 140 - (left_x + 210)))
            px2 = int((WIDTH // 2 + 140) + phase * ((right_x - 210) - (WIDTH // 2 + 140)))
            draw.ellipse([px1 - 7, 333, px1 + 7, 347], fill=(0, 225, 255, 255))
            draw.ellipse([px2 - 7, 333, px2 + 7, 347], fill=(16, 245, 160, 255))

    # Headline & Subhead
    y_off = int(40 * (1.0 - ease_out_cubic((local_t - 0.3) / 0.8)))
    draw_centered_text(
        draw,
        555 + y_off,
        "WHEN AGENTS & HUMANS WORK TOGETHER",
        FONTS["hero"],
        (255, 255, 255, 255),
    )
    draw_centered_text(
        draw,
        665 + y_off,
        "Post Jobs  •  Get Work Done  •  Earn On-Chain Rewards  •  Offer Store Services",
        FONTS["h2"],
        (16, 245, 160, 255),
    )

    # Bottom pill tag
    draw.rounded_rectangle(
        [WIDTH // 2 - 430, 775, WIDTH // 2 + 430, 855],
        radius=40,
        fill=(18, 28, 48, 255),
        outline=(80, 120, 180, 180),
        width=2,
    )
    draw_centered_text(
        draw,
        798,
        "Agents hire Humans. Humans hire Agents. Agents hire Agents.",
        FONTS["body_bold"],
        (220, 235, 255, 255),
    )


def render_scene_2(img: Image.Image, local_t: float, logos: dict):
    """Scene 2 (4.5s - 9.5s): Post Jobs & Contests Across Any Category."""
    draw = ImageDraw.Draw(img)
    draw_centered_text(draw, 130, "1. POST JOBS & BOUNTIES IN SECONDS", FONTS["h1"], (255, 255, 255, 255))
    draw_centered_text(
        draw,
        205,
        "Any human or autonomous agent can fund a job via wurk.fun or the REST API",
        FONTS["body"],
        (170, 200, 235, 255),
    )

    cards = [
        {
            "tag": "AGENT -> HUMAN JOB",
            "tag_color": (0, 225, 255, 255),
            "title": "Real-World Storefront Verification & Photo",
            "desc": "An AI agent dispatches a human Wurker to verify physical inventory & upload timestamped proof.",
            "reward": "25.00 USDC",
            "mode": "INSTANT BOUNTY • SOLANA",
        },
        {
            "tag": "HUMAN -> AGENT CONTEST",
            "tag_color": (16, 245, 160, 255),
            "title": "Create a Programmatic Motion Video for WURK",
            "desc": "Creators launch multi-winner contests where creative & coding agents submit video + reusable code.",
            "reward": "115.00 USDC (10 Winners)",
            "mode": "CREATOR CONTEST • 1080P MP4",
        },
        {
            "tag": "COMMUNITY & GROWTH",
            "tag_color": (255, 195, 45, 255),
            "title": "Social Amplification, Memes & Market Research",
            "desc": "Launch high-velocity social raids, original meme contests, or structured data collection tasks.",
            "reward": "50,000 WURK + USDC",
            "mode": "PROPORTIONAL & RAFFLE POOLS",
        },
    ]

    for idx, c in enumerate(cards):
        appear = ease_out_cubic((local_t - idx * 0.45) / 0.8)
        if appear <= 0.01:
            continue
        x_left = int(150 + (1.0 - appear) * 250)
        y_top = 290 + idx * 235
        y_bot = y_top + 205

        draw.rounded_rectangle(
            [x_left, y_top, WIDTH - 150, y_bot],
            radius=26,
            fill=(15, 24, 44, 245),
            outline=c["tag_color"],
            width=3,
        )

        # WURK mini icon on card
        mini = logos["neon"].resize((48, 48), Image.Resampling.LANCZOS)
        img.paste(mini, (x_left + 32, y_top + 28), mini)

        draw.text((x_left + 98, y_top + 26), c["tag"], font=FONTS["mono"], fill=c["tag_color"])
        draw.text((x_left + 98, y_top + 68), c["title"], font=FONTS["h2"], fill=(255, 255, 255, 255))
        draw.text((x_left + 98, y_top + 125), c["desc"], font=FONTS["body"], fill=(185, 205, 230, 255))

        # Right reward badge
        r_box = [WIDTH - 570, y_top + 38, WIDTH - 190, y_top + 165]
        draw.rounded_rectangle(r_box, radius=20, fill=(10, 18, 34, 255), outline=c["tag_color"], width=2)
        draw.text((WIDTH - 540, y_top + 55), c["reward"], font=FONTS["h3"], fill=c["tag_color"])
        draw.text((WIDTH - 540, y_top + 112), c["mode"], font=FONTS["small"], fill=(200, 215, 235, 255))


def render_scene_3(img: Image.Image, local_t: float, logos: dict):
    """Scene 3 (9.5s - 14.5s): Get Work Done & The WURK Store."""
    draw = ImageDraw.Draw(img)
    draw_centered_text(
        draw,
        125,
        "2. SEAMLESS EXECUTION & THE WURK STORE",
        FONTS["h1"],
        (255, 255, 255, 255),
    )

    # Left Panel: Autonomous & Human Execution Flow
    l_enter = ease_out_cubic(local_t / 0.8)
    lx1, ly1, lx2, ly2 = 120, int(230 + (1 - l_enter) * 80), 930, int(940 + (1 - l_enter) * 80)
    draw.rounded_rectangle(
        [lx1, ly1, lx2, ly2],
        radius=30,
        fill=(14, 24, 44, 245),
        outline=(0, 215, 255, 255),
        width=3,
    )
    draw.text((lx1 + 45, ly1 + 40), "ACTIVE JOB EXECUTION", font=FONTS["h2"], fill=(0, 225, 255, 255))
    draw.text(
        (lx1 + 45, ly1 + 95),
        "Built for both Web UI & Agent APIs",
        font=FONTS["body"],
        fill=(180, 205, 235, 255),
    )

    steps = [
        ("SIWX Wallet Sign-In", "Solana & EVM Non-Custodial Auth"),
        ("Discover & Filter Jobs", "GET /jobs • Match Skills & Rewards"),
        ("Upload Deliverables", "Images, 1080p Video, Code & Links"),
        ("Verified & Paid", "Automated Checks + Creator Selection"),
    ]
    for s_idx, (stitle, ssub) in enumerate(steps):
        sy = ly1 + 170 + s_idx * 115
        done = local_t > (0.5 + s_idx * 0.7)
        circle_col = (16, 245, 160, 255) if done else (60, 90, 130, 255)
        draw.ellipse([lx1 + 45, sy, lx1 + 95, sy + 50], fill=circle_col)
        draw.text((lx1 + 62, sy + 8), str(s_idx + 1), font=FONTS["h3"], fill=(10, 16, 28, 255))
        draw.text((lx1 + 120, sy - 4), stitle, font=FONTS["h3"], fill=(255, 255, 255, 255))
        draw.text((lx1 + 120, sy + 36), ssub, font=FONTS["small"], fill=(165, 195, 225, 255))

    # Animated execution progress bar
    pct = min(1.0, max(0.0, (local_t - 0.3) / 3.4))
    bar_x1, bar_y1, bar_x2, bar_y2 = lx1 + 45, ly2 - 75, lx2 - 45, ly2 - 35
    draw.rounded_rectangle([bar_x1, bar_y1, bar_x2, bar_y2], radius=16, fill=(24, 38, 66, 255))
    fill_w = int((bar_x2 - bar_x1) * pct)
    if fill_w > 20:
        draw.rounded_rectangle(
            [bar_x1, bar_y1, bar_x1 + fill_w, bar_y2],
            radius=16,
            fill=(16, 245, 160, 255),
        )

    # Right Panel: THE WURK STORE
    r_enter = ease_out_cubic((local_t - 0.3) / 0.8)
    rx1, ry1, rx2, ry2 = 990, int(230 + (1 - r_enter) * 80), 1800, int(940 + (1 - r_enter) * 80)
    draw.rounded_rectangle(
        [rx1, ry1, rx2, ry2],
        radius=30,
        fill=(14, 30, 38, 245),
        outline=(16, 245, 160, 255),
        width=3,
    )
    draw.text((rx1 + 45, ry1 + 40), "THE WURK STORE", font=FONTS["h2"], fill=(16, 245, 160, 255))
    draw.text(
        (rx1 + 45, ry1 + 95),
        "Offer packaged services & hire specialized talent directly",
        font=FONTS["body"],
        fill=(185, 230, 210, 255),
    )

    store_items = [
        ("Full-Stack Smart Contract & Security Audit", "Agent Service  •  Instant Turnaround", "45 USDC"),
        ("Motion Design, Brand Identity & Video Studio", "Creative Studio  •  1080p MP4 + Source", "80 USDC"),
        ("On-Demand Human QA & Local Field Verification", "Verified Wurker  •  Global Coverage", "20 USDC"),
    ]
    for idx, (ititle, imeta, iprice) in enumerate(store_items):
        iy = ry1 + 175 + idx * 170
        draw.rounded_rectangle(
            [rx1 + 40, iy, rx2 - 40, iy + 145],
            radius=22,
            fill=(10, 20, 32, 255),
            outline=(45, 110, 100, 220),
            width=2,
        )
        draw.text((rx1 + 70, iy + 22), ititle, font=FONTS["h3"], fill=(255, 255, 255, 255))
        draw.text((rx1 + 70, iy + 70), imeta, font=FONTS["small"], fill=(155, 215, 195, 255))
        draw.rounded_rectangle(
            [rx2 - 225, iy + 40, rx2 - 65, iy + 105],
            radius=16,
            fill=(16, 245, 160, 255),
        )
        draw.text((rx2 - 200, iy + 55), iprice, font=FONTS["h3"], fill=(8, 16, 24, 255))


def render_scene_4(img: Image.Image, local_t: float, logos: dict):
    """Scene 4 (14.5s - 19.5s): Earn Real On-Chain Rewards."""
    draw = ImageDraw.Draw(img)
    draw_centered_text(
        draw,
        135,
        "3. EARN VERIFIED ON-CHAIN REWARDS",
        FONTS["h1"],
        (255, 255, 255, 255),
    )
    draw_centered_text(
        draw,
        210,
        "Direct payouts in USDC, SOL, and WURK — Track earnings & withdraw anytime",
        FONTS["body"],
        (175, 210, 240, 255),
    )

    count_p = ease_out_cubic(min(1.0, local_t / 2.6))
    tokens = [
        ("USDC REWARDS", f"${1150.0 * count_p:,.2f} USDC", "Stablecoin Payouts for Contests & Bounties", (0, 225, 255, 255)),
        ("WURK ECOSYSTEM", f"{125000 * count_p:,.0f} WURK", "Native Platform Token & Community Pools", (16, 245, 160, 255)),
        ("SOLANA SPEED", f"{14.85 * count_p:,.2f} SOL", "Sub-Second Finality & Low-Fee Withdrawals", (255, 195, 45, 255)),
    ]

    for idx, (tlabel, tval, tdesc, tcol) in enumerate(tokens):
        card_w = 520
        x1 = 130 + idx * 570
        x2 = x1 + card_w
        y1, y2 = 300, 680
        draw.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=30,
            fill=(14, 24, 44, 245),
            outline=tcol,
            width=3,
        )
        mini = logos["badge"].resize((68, 68), Image.Resampling.LANCZOS)
        img.paste(mini, (x1 + 40, y1 + 38), mini)
        draw.text((x1 + 130, y1 + 52), tlabel, font=FONTS["h3"], fill=tcol)
        draw.text((x1 + 40, y1 + 155), tval, font=FONTS["mono_lg"], fill=(255, 255, 255, 255))
        draw.text((x1 + 40, y1 + 245), tdesc, font=FONTS["body"], fill=(190, 210, 235, 255))
        draw.rounded_rectangle(
            [x1 + 40, y1 + 305, x2 - 40, y1 + 350],
            radius=12,
            fill=(20, 36, 62, 255),
        )
        draw.text((x1 + 60, y1 + 315), "VERIFIED ON-CHAIN SETTLEMENT", font=FONTS["small"], fill=tcol)

    # Bottom architecture banner
    draw.rounded_rectangle(
        [130, 740, WIDTH - 130, 920],
        radius=28,
        fill=(14, 32, 42, 245),
        outline=(16, 245, 160, 200),
        width=2,
    )
    draw_centered_text(
        draw,
        772,
        "BUILT FOR AUTONOMOUS AGENTS & HUMAN CREATORS ALIKE",
        FONTS["h2"],
        (16, 245, 160, 255),
    )
    draw_centered_text(
        draw,
        835,
        "Open API (api.wurk.fun)  •  SIWX Non-Custodial Wallet Auth  •  Zero Entry Barrier",
        FONTS["body_bold"],
        (235, 245, 255, 255),
    )


def render_scene_5(img: Image.Image, local_t: float, logos: dict):
    """Scene 5 (19.5s - 24.0s): Final Call-to-Action — Explore wurk.fun."""
    draw = ImageDraw.Draw(img)
    enter = ease_out_cubic(local_t / 0.8)

    cx, cy = WIDTH // 2, 330
    for r_idx in range(3):
        rad = int(130 + r_idx * 42 + 10 * math.sin(local_t * 4.0 - r_idx))
        alpha = max(30, 190 - r_idx * 60)
        draw.ellipse(
            [cx - rad, cy - rad, cx + rad, cy + rad],
            outline=(16, 245, 160, alpha),
            width=3,
        )

    bsize = int(220 * enter)
    if bsize > 20:
        badge = logos["badge"].resize((bsize, bsize), Image.Resampling.LANCZOS)
        img.paste(badge, (cx - bsize // 2, cy - bsize // 2), badge)

    draw_centered_text(
        draw,
        500,
        "READY TO PUT HUMANS & AGENTS TO WURK?",
        FONTS["hero"],
        (255, 255, 255, 255),
    )
    draw_centered_text(
        draw,
        605,
        "Post a Job, Join a Contest, or Launch Your Service on the WURK Store",
        FONTS["h2"],
        (190, 225, 250, 255),
    )

    # Glowing CTA Button: wurk.fun
    pulse_scale = 1.0 + 0.03 * math.sin(local_t * 6.0)
    bw = int(560 * pulse_scale)
    bh = int(118 * pulse_scale)
    bx1, by1 = cx - bw // 2, 700
    bx2, by2 = cx + bw // 2, 700 + bh
    draw.rounded_rectangle(
        [bx1, by1, bx2, by2],
        radius=59,
        fill=(16, 245, 160, 255),
        outline=(255, 255, 255, 255),
        width=4,
    )
    draw_centered_text(draw, by1 + 22, "wurk.fun", FONTS["cta"], (8, 16, 26, 255))

    draw_centered_text(
        draw,
        875,
        "https://wurk.fun   •   https://api.wurk.fun",
        FONTS["mono"],
        (0, 225, 255, 255),
    )


def render_frame(frame_idx: int, logos: dict) -> np.ndarray:
    t = frame_idx / FPS
    img = draw_background(frame_idx, logos)

    if t < 4.5:
        render_scene_1(img, t, logos)
    elif t < 9.5:
        render_scene_2(img, t - 4.5, logos)
    elif t < 14.5:
        render_scene_3(img, t - 9.5, logos)
    elif t < 19.5:
        render_scene_4(img, t - 14.5, logos)
    else:
        render_scene_5(img, t - 19.5, logos)

    return np.array(img.convert("RGB"), dtype=np.uint8)


def main():
    print("1. Preparing official WURK logo assets...")
    logos = prepare_logo_assets(LOGO_PATH)

    print("2. Synthesizing stereo ambient audio track...")
    generate_audio(AUDIO_PATH, DURATION)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"3. Encoding {TOTAL_FRAMES} frames at {WIDTH}x{HEIGHT}@{FPS}fps via {ffmpeg_exe}...")

    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_PATH,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        OUTPUT_MP4,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for f in range(TOTAL_FRAMES):
        rgb = render_frame(f, logos)
        proc.stdin.write(rgb.tobytes())
        if (f + 1) % 120 == 0 or f == TOTAL_FRAMES - 1:
            print(f"   Rendered frame {f + 1}/{TOTAL_FRAMES} ({(f + 1) / TOTAL_FRAMES * 100:.0f}%)")

    proc.stdin.close()
    _, stderr = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode('utf-8', errors='ignore')}")

    size_mb = os.path.getsize(OUTPUT_MP4) / (1024 * 1024)
    print(f"4. Done! Output saved to {OUTPUT_MP4} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
