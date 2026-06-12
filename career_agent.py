#!/usr/bin/env python3
"""
Career & Market Intelligence Agent v2
───────────────────────────────────────
Weekly Friday email covering real senior-level career intelligence:

  - 🏢 Market signals — funding, expansions, leadership moves in UAE fintech
  - 📈 Skill trends — what senior engineers in Dubai need right now
  - 💰 Salary benchmark — current market rates for your level
  - 🧠 Weekly insight — one actionable career observation

First Monday of month additionally includes:
  - ✍️  LinkedIn post draft — builds inbound interest over time
  - 📨  Recruiter outreach draft — one warm message ready to send

Profile: Tech Lead AVP · Java · Kafka · Microservices · Spring Boot
         Kubernetes · AWS · BaaS · Fintech · Dubai
"""

import os
import json
import csv
import smtplib
import datetime
import anthropic

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

PROFILE = {
    "current_title":    "Tech Lead AVP",
    "current_company":  "Mashreq NEO",
    "domain":           "Fintech, BaaS, Customer Value Management, Microservices",
    "skills": [
        "Java", "Spring Boot", "Spring AI", "Kafka", "Kubernetes",
        "AWS", "Microservices", "REST APIs", "BaaS", "Event-driven architecture",
        "Docker", "CI/CD", "Agile", "Technical leadership"
    ],
    "target_roles": [
        "Principal Engineer",
        "Tech Lead",
        "AVP Engineering",
        "Staff Engineer",
        "Engineering Manager"
    ],
    "location":         "Dubai, UAE",
    "min_salary_aed":   38000,
    "years_experience": 10,
    "sectors":          ["Fintech", "Banking", "Payments", "Neobank", "BaaS"],
}

LOG_FILE = "career_log.csv"


# ─────────────────────────────────────────────────────────────────────────────
# DATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def is_first_monday_of_month(date: datetime.date) -> bool:
    if date.weekday() != 0:
        return False
    return date.day <= 7


def get_week_range(date: datetime.date) -> str:
    start = date - datetime.timedelta(days=date.weekday())
    end   = start + datetime.timedelta(days=4)
    return f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}"


# ─────────────────────────────────────────────────────────────────────────────
# CLAUDE AGENT
# ─────────────────────────────────────────────────────────────────────────────

def call_career_agent(include_monthly: bool) -> dict:
    print("  Calling Claude career agent with web search...")

    client     = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today      = datetime.date.today()
    week_range = get_week_range(today)
    skills_str = ", ".join(PROFILE["skills"])
    roles_str  = ", ".join(PROFILE["target_roles"])
    sectors_str= ", ".join(PROFILE["sectors"])

    monthly_instruction = ""
    if include_monthly:
        monthly_instruction = """
MONTHLY ADDITIONS (include only on first Monday of month):

1. LINKEDIN POST:
Draft a LinkedIn post for a Tech Lead AVP in Dubai fintech.
Rules:
- Based on a real trend or insight from your market research above
- Direct and practical — sounds like a senior engineer, not a marketer
- 150-200 words
- Ends with a genuine question to drive comments
- 4-5 relevant hashtags
- Must reference something specific and real from this week's data

Include in JSON:
"monthly": {
  "linkedin_post": {
    "angle": "one line describing the post angle",
    "draft": "full post text",
    "hashtags": ["#tag1", "#tag2"]
  }
}
"""

    prompt = f"""You are a career intelligence analyst for a senior software engineer in Dubai.
Today is {today} (Week: {week_range}).

ENGINEER PROFILE:
- Title: {PROFILE['current_title']} at {PROFILE['current_company']}
- Skills: {skills_str}
- Target roles: {roles_str}
- Domain: {PROFILE['domain']}
- Location: {PROFILE['location']}
- Min salary: AED {PROFILE['min_salary_aed']:,}/month
- Sectors: {sectors_str}
- Years experience: {PROFILE['years_experience']}+

IMPORTANT CONTEXT:
This engineer is NOT actively job hunting. At Principal/AVP level in Dubai fintech,
roles come through recruiters and networks — not job boards. Do NOT search job listings.
Instead focus on market intelligence that matters at this level.

YOUR TASK:
Use web search to find this week's relevant market signals. Search for:
1. UAE/Dubai fintech funding rounds, acquisitions, or expansions announced this week
2. Engineering leadership moves in Dubai/UAE fintech — CTOs, VPs, Heads of Engineering changing roles
3. New fintech products or platform launches in UAE that signal engineering headcount growth
4. Skill demand signals — what technical skills are senior fintech engineers in UAE/Gulf being asked about
5. Salary intelligence for Principal Engineer / Tech Lead level in Dubai
6. Any notable UAE fintech news that a senior engineer should be aware of this week

{monthly_instruction}

Produce a JSON response with this exact structure:
{{
  "week": "{week_range}",
  "date": "{today}",
  "market_pulse": "one sentence summary of UAE fintech market this week",
  "market_signals": [
    {{
      "company": "company name",
      "signal_type": "Funding / Expansion / Leadership Move / Product Launch / Acquisition",
      "headline": "what happened — be specific and factual",
      "why_it_matters": "what this means for senior engineering hiring in this company",
      "career_relevance": "High / Medium / Low",
      "source": "publication name"
    }}
  ],
  "skill_trends": {{
    "rising": ["skill 1", "skill 2"],
    "stable": ["skill 1", "skill 2"],
    "fading": ["skill 1"],
    "insight": "one sentence — what this means for this specific engineer"
  }},
  "salary_benchmark": {{
    "principal_engineer": "AED X-Y/month",
    "tech_lead_avp": "AED X-Y/month",
    "staff_engineer": "AED X-Y/month",
    "trend": "Stable / Rising / Falling",
    "note": "any useful salary context"
  }},
  "weekly_insight": "2-3 sentences of sharp, specific career intelligence for this engineer this week — not generic advice",
  "monthly": null
}}

If include_monthly is false, set monthly to null.
Respond ONLY with valid JSON, no preamble or markdown backticks."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    print("  ✓ Claude response received")

    try:
        start = full_text.find("{")
        end   = full_text.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(full_text[start:end])
            print(f"  ✓ Parsed: {result.get('market_pulse', 'N/A')[:70]}...")
            return result
    except Exception as e:
        print(f"  ✗ JSON parse error: {e}")

    return {
        "week":           week_range,
        "date":           str(today),
        "market_pulse":   "Data unavailable this week.",
        "market_signals": [],
        "skill_trends":   {"rising": [], "stable": [], "fading": [], "insight": ""},
        "salary_benchmark": {"principal_engineer": "N/A", "tech_lead_avp": "N/A",
                             "staff_engineer": "N/A", "trend": "N/A", "note": ""},
        "weekly_insight": "Agent encountered an error. Please check logs.",
        "monthly":        None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# EMAIL BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_email_html(data: dict, include_monthly: bool) -> str:

    week           = data.get("week", "")
    market_pulse   = data.get("market_pulse", "")
    signals        = data.get("market_signals", [])
    skill_trends   = data.get("skill_trends", {})
    salary         = data.get("salary_benchmark", {})
    weekly_insight = data.get("weekly_insight", "")
    monthly        = data.get("monthly")

    # ── Signal type colours
    signal_colors = {
        "Funding":         ("#7c3aed", "#ede9fe"),
        "Expansion":       ("#2563eb", "#dbeafe"),
        "Leadership Move": ("#ca8a04", "#fef9c3"),
        "Product Launch":  ("#16a34a", "#dcfce7"),
        "Acquisition":     ("#dc2626", "#fee2e2"),
    }

    relevance_colors = {
        "High":   ("#16a34a", "#dcfce7"),
        "Medium": ("#ca8a04", "#fef9c3"),
        "Low":    ("#9ca3af", "#f3f4f6"),
    }

    # ── Market signals rows
    signal_rows = ""
    for s in signals[:6]:
        stype      = s.get("signal_type", "")
        sc, sb     = signal_colors.get(stype, ("#6b7280", "#f3f4f6"))
        rel        = s.get("career_relevance", "Medium")
        rc, rb     = relevance_colors.get(rel, ("#9ca3af", "#f3f4f6"))
        signal_rows += f"""
        <tr>
          <td style="padding:14px 12px;border-bottom:1px solid #f3f4f6;vertical-align:top;">
            <div style="font-weight:700;color:#111827;font-size:13px;margin-bottom:4px;">
              {s.get('company', '')}
            </div>
            <span style="background:{sb};color:{sc};padding:2px 8px;border-radius:4px;
                         font-size:10px;font-weight:700;text-transform:uppercase;">{stype}</span>
          </td>
          <td style="padding:14px 12px;border-bottom:1px solid #f3f4f6;vertical-align:top;">
            <div style="color:#111827;font-size:13px;margin-bottom:4px;">
              {s.get('headline', '')}
            </div>
            <div style="color:#6b7280;font-size:12px;">
              {s.get('why_it_matters', '')}
            </div>
            <div style="color:#9ca3af;font-size:11px;margin-top:4px;">
              via {s.get('source', '')}
            </div>
          </td>
          <td style="padding:14px 12px;border-bottom:1px solid #f3f4f6;
                     text-align:center;vertical-align:top;white-space:nowrap;">
            <span style="background:{rb};color:{rc};padding:2px 8px;border-radius:4px;
                         font-size:11px;font-weight:700;">{rel}</span>
          </td>
        </tr>"""

    if not signal_rows:
        signal_rows = """<tr><td colspan="3" style="padding:16px;text-align:center;
                         color:#9ca3af;font-size:13px;">No significant signals found this week.</td></tr>"""

    # ── Skill tags
    def skill_tags(skills, color, bg):
        return "".join(
            f'<span style="background:{bg};color:{color};padding:3px 10px;border-radius:12px;'
            f'font-size:12px;font-weight:600;margin:3px 3px 3px 0;display:inline-block;">{s}</span>'
            for s in skills
        )

    rising_tags = skill_tags(skill_trends.get("rising", []), "#16a34a", "#dcfce7")
    stable_tags = skill_tags(skill_trends.get("stable", []), "#2563eb", "#dbeafe")
    fading_tags = skill_tags(skill_trends.get("fading", []), "#9ca3af", "#f3f4f6")

    # ── Monthly section
    monthly_section = ""
    if include_monthly and monthly:
        li_post   = monthly.get("linkedin_post", {})
        li_draft      = li_post.get("draft", "").replace("\n", "<br>")
        li_angle      = li_post.get("angle", "")
        li_hashtags   = " ".join(li_post.get("hashtags", []))
        monthly_section = f"""
    <!-- LinkedIn Post -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;background:#fafaf9;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:6px;">✍️ Monthly LinkedIn Draft</div>
      <div style="color:#6b7280;font-size:12px;margin-bottom:14px;">
        Angle: <em>{li_angle}</em>
      </div>
      <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;
                  padding:16px 20px;font-size:13px;color:#374151;line-height:1.8;">
        {li_draft}
      </div>
      <div style="margin-top:8px;color:#9ca3af;font-size:12px;">{li_hashtags}</div>
      <div style="margin-top:6px;color:#9ca3af;font-size:11px;">
        ↑ Add one specific personal detail before posting — makes it yours.
      </div>
    </div>

"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f9fafb;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">

  <div style="max-width:700px;margin:32px auto;background:#ffffff;border-radius:12px;
               overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e1b4b 0%,#4f46e5 100%);padding:28px 32px;">
      <div style="color:#a5b4fc;font-size:12px;font-weight:600;letter-spacing:1px;
                  text-transform:uppercase;">Career Intelligence Agent v2</div>
      <div style="color:#ffffff;font-size:22px;font-weight:700;margin-top:4px;">
        Weekly Brief · {week}
      </div>
      <div style="color:#c7d2fe;font-size:14px;margin-top:8px;line-height:1.6;">
        {market_pulse}
      </div>
    </div>

    <!-- Market Signals -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:12px;">🏢 Market Signals This Week</div>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;width:160px;">Company</th>
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">What Happened & Why It Matters</th>
            <th style="padding:8px 12px;text-align:center;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;width:80px;">Relevance</th>
          </tr>
        </thead>
        <tbody>{signal_rows}</tbody>
      </table>
    </div>

    <!-- Skill Trends -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:14px;">📈 Skill Trends · Dubai Fintech</div>
      <div style="margin-bottom:10px;">
        <span style="font-size:11px;font-weight:700;color:#6b7280;
                     text-transform:uppercase;margin-right:8px;">Rising</span>
        {rising_tags or '<span style="color:#9ca3af;font-size:12px;">None notable</span>'}
      </div>
      <div style="margin-bottom:10px;">
        <span style="font-size:11px;font-weight:700;color:#6b7280;
                     text-transform:uppercase;margin-right:8px;">Stable</span>
        {stable_tags or '<span style="color:#9ca3af;font-size:12px;">N/A</span>'}
      </div>
      <div style="margin-bottom:14px;">
        <span style="font-size:11px;font-weight:700;color:#6b7280;
                     text-transform:uppercase;margin-right:8px;">Fading</span>
        {fading_tags or '<span style="color:#9ca3af;font-size:12px;">None notable</span>'}
      </div>
      <div style="background:#f8faff;border-left:3px solid #4f46e5;padding:10px 14px;
                  border-radius:0 6px 6px 0;color:#374151;font-size:13px;">
        💡 {skill_trends.get('insight', '')}
      </div>
    </div>

    <!-- Salary Benchmark -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:14px;">💰 Salary Benchmark · Dubai</div>
      <table style="width:100%;border-collapse:collapse;">
        <tr style="background:#f9fafb;">
          <td style="padding:10px 14px;font-size:13px;color:#374151;font-weight:600;
                     border-bottom:1px solid #f3f4f6;">Principal Engineer</td>
          <td style="padding:10px 14px;font-size:13px;color:#111827;font-weight:700;
                     border-bottom:1px solid #f3f4f6;">{salary.get('principal_engineer','N/A')}</td>
        </tr>
        <tr>
          <td style="padding:10px 14px;font-size:13px;color:#374151;font-weight:600;
                     border-bottom:1px solid #f3f4f6;">Tech Lead AVP</td>
          <td style="padding:10px 14px;font-size:13px;color:#111827;font-weight:700;
                     border-bottom:1px solid #f3f4f6;">{salary.get('tech_lead_avp','N/A')}</td>
        </tr>
        <tr style="background:#f9fafb;">
          <td style="padding:10px 14px;font-size:13px;color:#374151;font-weight:600;">
            Staff Engineer</td>
          <td style="padding:10px 14px;font-size:13px;color:#111827;font-weight:700;">
            {salary.get('staff_engineer','N/A')}</td>
        </tr>
      </table>
      <div style="margin-top:10px;color:#6b7280;font-size:12px;">
        Trend: <strong>{salary.get('trend','N/A')}</strong>
        {' · ' + salary.get('note','') if salary.get('note') else ''}
      </div>
    </div>

    <!-- Weekly Insight -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;background:#f8faff;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:10px;">🧠 This Week's Insight</div>
      <p style="margin:0;color:#1e1b4b;font-size:14px;line-height:1.7;font-weight:500;">
        {weekly_insight}
      </p>
    </div>

    {monthly_section}

    <!-- Footer -->
    <div style="padding:16px 32px;background:#f9fafb;">
      <p style="margin:0;font-size:11px;color:#9ca3af;text-align:center;">
        Career Intelligence Agent · Every Friday 08:00 UAE time<br>
        LinkedIn post draft on first Monday of each month
      </p>
    </div>

  </div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL LOG
# ─────────────────────────────────────────────────────────────────────────────

def append_career_log(data: dict, include_monthly: bool) -> None:
    headers = [
        "date", "week", "signals_found", "high_relevance_signals",
        "top_rising_skill", "salary_trend", "monthly_drafted", "market_pulse"
    ]

    signals       = data.get("market_signals", [])
    high_rel      = sum(1 for s in signals if s.get("career_relevance") == "High")
    rising_skills = data.get("skill_trends", {}).get("rising", [])
    top_skill     = rising_skills[0] if rising_skills else ""

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
            print(f"  ✓ Created career log: {LOG_FILE}")
        writer.writerow({
            "date":                 data.get("date", ""),
            "week":                 data.get("week", ""),
            "signals_found":        len(signals),
            "high_relevance_signals": high_rel,
            "top_rising_skill":     top_skill,
            "salary_trend":         data.get("salary_benchmark", {}).get("trend", ""),
            "monthly_drafted":      include_monthly,
            "market_pulse":         data.get("market_pulse", "")[:100],
        })
    print(f"  ✓ Career log updated for {data.get('date', '')}")


# ─────────────────────────────────────────────────────────────────────────────
# SEND EMAIL
# ─────────────────────────────────────────────────────────────────────────────

def send_email(html: str, data: dict, include_monthly: bool) -> None:
    sender    = os.environ["EMAIL_ADDRESS"]
    password  = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ.get("TO_EMAIL", sender)

    week     = data.get("week", "")
    signals  = data.get("market_signals", [])
    high_rel = sum(1 for s in signals if s.get("career_relevance") == "High")

    monthly_tag = " · 📝 LinkedIn Draft Ready" if include_monthly else ""
    subject = (
        f"🏢 Career Intel · {week} · "
        f"{high_rel} High-Relevance Signal{'s' if high_rel != 1 else ''}"
        f"{monthly_tag}"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Career Intelligence Agent <{sender}>"
    msg["To"]      = recipient
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"  ✓ Email sent → {recipient}")
    print(f"    Subject: {subject}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    today = datetime.date.today()
    print(f"\n{'─'*60}")
    print(f"  Career Intelligence Agent v2 · {today}")
    print(f"{'─'*60}\n")

    include_monthly = is_first_monday_of_month(today)
    print(f"[ CONFIG ] Week      : {get_week_range(today)}")
    print(f"[ CONFIG ] Monthly   : {include_monthly}")
    print()

    print("[ LAYER 1 ] Running market intelligence analysis...")
    data = call_career_agent(include_monthly)
    print()

    print("[ LAYER 2 ] Building and sending email...")
    html = build_email_html(data, include_monthly)
    send_email(html, data, include_monthly)
    print()

    print("[ LAYER 3 ] Logging...")
    append_career_log(data, include_monthly)

    print(f"\n{'─'*60}")
    print(f"  Agent complete · {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()
