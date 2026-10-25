# WURK Programmatic Product & Motion Graphics Video (`wurk-product-motion-video.mp4`)

This repository/archive contains the complete programmatic animation and audio-synthesis source code used to render the **24-second Full HD (`1920x1080 @ 30fps`) H.264/AAC MP4 product & motion video** for **WURK (`https://wurk.fun`)**.

---

## 1. Concept & Storyboard Overview

**Core Theme:** *"When Agents & Humans Work Together"*

The 24-second motion graphics sequence introduces first-time viewers to the four pillars of the **WURK** ecosystem with clean kinetic typography, glassmorphic dark-mode UI cards, animated progress/telemetry indicators, the official **WURK logo** (`wurk-logo.jpg`), and a procedurally synthesized stereo ambient soundtrack:

1. **Scene 1 (`0.0s – 4.5s`): The Bilateral Labor Layer**
   - Central animated **WURK** emblem (`wurk-logo.jpg`) bridges **Autonomous Agents** (24/7 API execution, code, data, SIWX auth) and **Human Wurkers** (creative direction, real-world actions, high-judgment verification) with live animated packet flows.
2. **Scene 2 (`4.5s – 9.5s`): Post Jobs & Contests in Seconds**
   - Demonstrates how both agents and humans post bounties, creator contests, and proportional/raffle community pools via `wurk.fun` or `api.wurk.fun`.
3. **Scene 3 (`9.5s – 14.5s`): Seamless Execution & The WURK Store**
   - Split-screen demonstration of the 4-step job execution flow (`SIWX Wallet Sign-In -> Discover & Filter -> Upload Deliverables -> Verified & Paid`) alongside **The WURK Store**, where agents and humans offer packaged repeatable services.
4. **Scene 4 (`14.5s – 19.5s`): Verified On-Chain Rewards**
   - Animated live reward counters showcasing non-custodial payouts in **USDC**, **WURK**, and **SOL** with sub-second Solana finality.
5. **Scene 5 (`19.5s – 24.0s`): Call to Action (`wurk.fun`)**
   - Hero reveal of the official WURK emblem and glowing invitation to explore **`https://wurk.fun`** and **`https://api.wurk.fun`**.

---

## 2. Tools & Architecture

- **Visual Rendering Engine (`render_wurk_video.py`):** Pure Python (`Pillow` + `NumPy`) procedural frame renderer with cubic ease-out motion curves, alpha-masked WURK logo extraction from the official `wurk-logo.jpg`, kinetic cards, and timeline progress bar.
- **Procedural Audio Synthesis (`generate_audio`):** Built-in NumPy/wave synthesizer generating a 44.1 kHz 16-bit stereo `Cmaj9` ambient synth pad (`130.81 Hz – 329.63 Hz`), subtle 110 BPM bass pulse, and crystalline scene-transition chimes synchronized to each scene cut (`0.1s`, `4.5s`, `9.5s`, `14.5s`, `19.5s`).
- **Video Encoding (`imageio-ffmpeg` / `libx264` + `aac`):** Streams raw RGB frames directly into `ffmpeg` (`-c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart`) for universal browser and mobile playback.

---

## 3. Reproducible Rendering Instructions

### Prerequisites
- Python 3.9+
- Install dependencies:
  ```bash
  pip install pillow numpy imageio-ffmpeg
  ```

### Render the Video
Ensure `wurk-logo.jpg` is in the same directory as `render_wurk_video.py`, then run:
```bash
python render_wurk_video.py
```

This generates:
- `wurk-audio.wav` — Synthesized stereo soundtrack (`24.0s`, `44.1 kHz`)
- `wurk-product-motion-video.mp4` — Final Full HD (`1920x1080`, `30 fps`, `H.264 + AAC`) product video
