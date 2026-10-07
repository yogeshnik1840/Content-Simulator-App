import re
from io import BytesIO

import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

PLATFORMS = ["Instagram", "YouTube", "Facebook", "Telegram", "WhatsApp"]
MEDIA_TYPES = ["Image/Graphic Thumbnail", "Vertical Video (Reels/Shorts)", "Horizontal Video", "No Media / Text Only"]
VIDEO_TYPES = ["Vertical Video (Reels/Shorts)", "Horizontal Video"]

DEFAULT_TITLE = "How to scale your business by 10x using AI"
DEFAULT_BODY = "Stop doing manual work. Here is the exact framework we used to save 40+ hours this week..."
DEFAULT_MEDIA = "https://picsum.photos/800/500"

PRESETS = {
    "E-commerce Brand Reel": {
        "platform": "Instagram",
        "title_input": "",
        "content_text": "Our best-selling tote just got a glow-up. Tap to see the 3 colors dropping this Friday...",
        "media_type": "Vertical Video (Reels/Shorts)",
        "media_url": "https://picsum.photos/600/900",
    },
    "B2B Founder Long-form YT": {
        "platform": "YouTube",
        "title_input": "How I Built a $1M ARR B2B Company With a Team of 3",
        "content_text": "In this video I break down the exact systems, hires and tools behind our first $1M in recurring revenue.",
        "media_type": "Horizontal Video",
        "media_url": "https://picsum.photos/1280/720",
    },
    "SaaS Telegram Broadcast": {
        "platform": "Telegram",
        "title_input": "New Feature Drop: Automated Weekly Reports",
        "content_text": "Your weekly metrics now land in your inbox every Monday, no setup needed. Try it today.",
        "media_type": "Image/Graphic Thumbnail",
        "media_url": "https://picsum.photos/800/500",
    },
}

st.set_page_config(page_title="Omnichannel Creator Growth Simulator", layout="wide")

# ---------- session state defaults ----------
defaults = {
    "audit_results": None,
    "audit_is_sample": False,
    "platform": "Instagram",
    "title_input": DEFAULT_TITLE,
    "content_text": DEFAULT_BODY,
    "media_type": MEDIA_TYPES[0],
    "media_url": DEFAULT_MEDIA,
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)


def load_preset():
    preset = PRESETS.get(st.session_state["preset_choice"])
    if preset:
        for key, value in preset.items():
            st.session_state[key] = value
        st.session_state["audit_results"] = None


st.title("🚀 Omnichannel Creator Growth Simulator & AI Strategist")
st.caption("Showcase your visual content across 5 major platforms and get instant algorithmic optimization reports.")

with st.sidebar:
    st.header("🔑 Configuration")
   default_api_key = st.secrets.get("GEMINI_API_KEY", "")

gemini_api_key = st.text_input(
    "Google AI Studio API Key",
    value=default_api_key,
    type="password",
    help="Enter your Gemini API Key to unlock real-time optimization updates.",
)
    st.divider()
    st.markdown("### 💼 Portfolio Quick-Load")
    st.selectbox(
        "Load Example Case Study",
        ["None"] + list(PRESETS.keys()),
        key="preset_choice",
        on_change=load_preset,
    )

platform = st.selectbox("🌐 Choose Platform Simulator", PLATFORMS, key="platform")

col1, col2 = st.columns([1, 1])


def show_media(url, kind, width=None):
    """Render an image or video; fail gracefully on bad URLs."""
    if not url:
        st.caption("No media URL provided.")
        return
    try:
        if kind in VIDEO_TYPES:
            st.video(url)
        elif width:
            st.image(url, width=width)
        else:
            st.image(url, use_container_width=True)
    except Exception:
        st.warning("Could not load media from that URL.")


with col1:
    st.subheader(f"📱 {platform} Mockup Input")

    title_input = ""
    if platform in ["YouTube", "Facebook", "Telegram"]:
        title_input = st.text_input("Post / Video Title", key="title_input")

    content_text = st.text_area("Caption / Message Body", height=150, key="content_text")
    media_type = st.radio("Media Type", MEDIA_TYPES, key="media_type")
    media_url = st.text_input("Media URL (Image or Direct Video Link)", key="media_url")
    has_media = media_type != "No Media / Text Only"

    st.markdown("### 🖥️ Live Simulator View")
    with st.container(border=True):
        if platform == "Instagram":
            st.markdown("**👤 your_brand** • Following")
            if has_media:
                show_media(media_url, media_type)
            st.markdown("❤️ 💬 ✈️")
            st.markdown(f"**your_brand** {content_text}")

        elif platform == "YouTube":
            if media_type == "Vertical Video (Reels/Shorts)":
                st.markdown("**📱 YouTube Shorts Mode**")
                show_media(media_url, media_type)
                st.markdown(f"🔊 💬 👍 **{title_input}**")
            else:
                if has_media:
                    show_media(media_url, media_type)
                st.markdown(f"### {title_input}")
                st.markdown("👤 **Channel Name** • 120K subscribers • 1 hour ago")
                st.caption(content_text)

        elif platform == "Facebook":
            st.markdown("🌐 **Your Business Page** • Public")
            if title_input:
                st.markdown(f"**{title_input}**")
            st.write(content_text)
            if has_media:
                show_media(media_url, media_type)
            st.divider()
            st.markdown("👍 Like  💬 Comment  ↪️ Share")

        elif platform == "Telegram":
            st.markdown("📢 **🎯 Growth Secrets Channel** (Broadcast View)")
            with st.chat_message("assistant", avatar="🎯"):
                if title_input:
                    st.markdown(f"### {title_input}")
                st.write(content_text)
                if has_media:
                    show_media(media_url, media_type, width=400)
                st.caption("👁️ 4.2K views   10:14 AM")

        elif platform == "WhatsApp":
            st.markdown("🟢 **VIP Business Alerts Group**")
            with st.chat_message("user", avatar="💬"):
                st.markdown("**💡 Strategy Broadcast**")
                st.write(content_text)
                if has_media:
                    show_media(media_url, media_type, width=300)
                st.caption("10:14 AM ✔️✔️")

# ---------- sample reports (shown when no API key / API failure) ----------
dummy_reports = {
    "Instagram": "### ⚡ THE HOOK OVERHAUL\n- **Current:** Stop doing manual work...\n- **Hook 1 (Curiosity):** The hidden AI workflow that saves 40 hours a week.\n- **Hook 2 (Negative):** Stop wasting 5 days a month on repetitive tasks.\n- **Hook 3 (Authority):** The exact system we use to run a $10k business on autopilot.\n\n### 📈 CAPTION OPTIMIZATION\n- **Attention:** If you're still working manually, you're losing money.\n- **Interest:** This 3-step AI workflow cuts execution time in half.\n- **Desire:** Imagine saving a full workweek every single month to focus purely on scale.\n- **CTA:** Comment 'SCALE' below and I'll DM you the setup blueprint!\n\n### 🎬 VISUAL EDITING & RETENTION SECRETS\n1. **Flash Hack:** Use text pop-ups on screen every 2.5 seconds during the video introduction.\n2. **Pattern Interrupt:** Zoom in 10% exactly at second 4 to emphasize the core framework text.\n3. **Loop:** End the script with 'And that's why you should...' to smoothly loop back to the hook.\n\n### 📊 PERFORMANCE SCORE\n- **Growth Potential Score:** 88/100\n- **Bottleneck:** The call-to-action relies too much on link clicks; switching to comment automation will boost algorithm visibility.",
    "YouTube": "### 🖼️ CTR & THUMBNAIL AUDIT\n- **Title 1:** I Automated 90% of My Business (Here's How)\n- **Title 2:** The 40-Hour AI Workflow\n- **Title 3:** Stop Working Harder Than AI\n\n### ⏱️ THE 30-SECOND RETENTION HOOK\n- Start directly on an active frame showing a live dashboard moving at 2x speed. Say: 'This single asset saved us exactly 42 hours this week, without hiring a single Virtual Assistant.' Avoid generic welcoming intros.\n\n### 🔍 SEO & DESCRIPTION OPTIMIZATION\n- Optimize for: Business automation tools, scale business using AI, productivity systems.\n- **CTA:** Pin a comment linking straight to your strategy discovery portal.\n\n### 📈 YT PERFORMANCE SCORE\n- **Projected Score:** 82/100\n- **Tactical Tip:** Cut out all breathing breaks and use immediate dynamic graphic inserts.",
    "Facebook": "### 📢 SHAREABILITY REPORT\n- Ask users to tag one friend who desperately needs to automate their back office workflows.\n\n### 📊 PERFORMANCE SCORE\n- **Virality Score:** 76/100",
    "Telegram": "### ⚡ SCANNABILITY ANALYSIS\n- Add customized emojis to break up long sentence sequences.\n\n### 📊 PERFORMANCE SCORE\n- **Link Click-Through Score:** 84/100",
    "WhatsApp": "### 🟢 DIRECT MESSAGE CONVERSION REPORT\n- Keep it highly intimate. Strip all corporate speak.\n\n### 📊 PERFORMANCE SCORE\n- **Response Rate Prediction:** 91/100",
}


# ---------- PDF helpers ----------
def clean_for_pdf(text):
    # Remove emojis / symbols the built-in Helvetica font can't draw
    text = re.sub(r"[^\x00-\x7F\u00A0-\u00FF\u2013\u2014\u2018\u2019\u201C\u201D\u2022]", "", text)
    # Escape characters ReportLab would read as markup
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Markdown bold -> ReportLab bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text.strip()


def generate_pdf_report(platform_name, content_body):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="AI Growth Strategy Report")
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=20,
                                 spaceAfter=18, textColor=colors.HexColor("#1A73E8"))
    heading_style = ParagraphStyle("SectionHeading", parent=styles["Heading2"], fontSize=13,
                                   spaceBefore=12, spaceAfter=8, textColor=colors.HexColor("#202124"))
    body_style = ParagraphStyle("ReportBody", parent=styles["BodyText"], fontSize=10,
                                leading=14, spaceAfter=6)
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8,
                                  textColor=colors.gray, alignment=1)

    story = [Paragraph(f"{platform_name} Content Growth Strategy Report", title_style), Spacer(1, 10)]

    for raw in content_body.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if line.startswith("###"):
            story.append(Paragraph(clean_for_pdf(line.lstrip("#")), heading_style))
        elif re.match(r"^[-*]\s", line):
            story.append(Paragraph("• " + clean_for_pdf(line[2:]), body_style))
        else:
            story.append(Paragraph(clean_for_pdf(line), body_style))

    story += [Spacer(1, 15), Paragraph("Generated via Omnichannel Content Growth Simulator.", footer_style)]
    doc.build(story)
    buffer.seek(0)
    return buffer


# ---------- Gemini call ----------
def run_gemini_audit(api_key, platform, title, body, media):
    system_instruction = (
        "You are an elite Cross-Platform Growth Strategist and Copywriter. "
        "Evaluate the target platform and optimize the copy directly. "
        "Always return distinct clear headings starting with '###' and use concise bullet points. "
        "Do not include markdown bold formatting inside headings."
    )
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Platform: {platform}\n"
                    f"Title Context: {title}\n"
                    f"Content to evaluate: {body}\n"
                    f"Media Type: {media}"
                )
            }]
        }],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
    }
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=60)
    try:
        data = response.json()
    except ValueError:
        data = {}

    if response.status_code != 200:
        message = data.get("error", {}).get("message", response.text[:200])
        raise RuntimeError(message)

    candidates = data.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        raise RuntimeError("Gemini returned no content (the response may have been blocked).")
    return text


with col2:
    st.subheader("📊 AI Optimization Strategy Insights")
    analyze_btn = st.button("✨ Run Algorithmic Content Audit", type="primary")

    if analyze_btn:
        sample = dummy_reports.get(platform, "No audit available.")
        if gemini_api_key:
            with st.spinner(f"Analyzing with {GEMINI_MODEL}..."):
                try:
                    st.session_state["audit_results"] = run_gemini_audit(
                        gemini_api_key, platform, title_input, content_text, media_type
                    )
                    st.session_state["audit_is_sample"] = False
                except Exception as e:
                    st.error(f"Gemini API error: {e}")
                    st.session_state["audit_results"] = sample
                    st.session_state["audit_is_sample"] = True
        else:
            st.info("💡 No API key detected in the sidebar. Showing a sample audit report.")
            st.session_state["audit_results"] = sample
            st.session_state["audit_is_sample"] = True

    if st.session_state["audit_results"]:
        if st.session_state["audit_is_sample"]:
            st.caption("⚠️ Sample report (not generated from your content).")
        st.markdown(st.session_state["audit_results"])

        pdf_buffer = generate_pdf_report(platform, st.session_state["audit_results"])
        st.download_button(
            label="📥 Download Strategy PDF Report",
            data=pdf_buffer,
            file_name=f"{platform}_Growth_Audit.pdf",
            mime="application/pdf",
        )
