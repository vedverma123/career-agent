#!/usr/bin/env python3
"""
Career & Market Intelligence Agent
────────────────────────────────────
Weekly Friday email covering:
  - Dubai fintech job market — roles matching your profile
  - Skill trends — what's rising, stable, fading in JDs
  - Salary benchmarks — senior engineering in Dubai
  - Companies to watch — who's hiring and scaling

First Monday of month additionally includes:
  - LinkedIn post draft based on market observations

Profile: Tech Lead AVP · Java · Kafka · Microservices · Spring Boot
         Kubernetes · AWS · BaaS · Fintech · Dubai
"""

import os
import json
import csv
import smtplib
import datetime
import calendar
import anthropic

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────────────────────────────────────
# PROFILE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

PROFILE = {
    "current_title":   "Tech Lead AVP",
    "current_company": "Mashreq NEO",
    "domain":          "Fintech, BaaS, Customer Value Management, Microservices",
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
    "location":        "Dubai, UAE",
    "min_salary_aed":  38000,
    "years_experience": 10,
    "sectors":         ["Fintech", "Banking", "Payments", "Neobank", "BaaS"],
}

LOG_FILE = "career_log.csv"


# ─────────────────────────────────────────────────────────────────────────────
# DATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def is_first_monday_of_month(date: datetime.date) -> bool:
    """Returns True if date is the first Monday of its month."""
    if date.weekday() != 0:  # 0 = Monday
        return False
    return date.day <= 7


def get_week_range(date: datetime.date) -> str:
    """Returns a human-readable week range string."""
    start = date - datetime.timedelta(days=date.weekday())
    end   = start + datetime.timedelta(days=4)
    return f"{start.strftime('%d %b')} – {end.strftime('%d %b %Y')}"


# ─────────────────────────────────────────────────────────────────────────────
# CLAUDE AGENT — WEEKLY MARKET ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def call_career_agent(include_linkedin: bool) -> dict:
    """Call Claude with web search for career market intelligence."""
    print("  Calling Claude career agent with web search...")

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today      = datetime.date.today()
    week_range = get_week_range(today)

    skills_str  = ", ".join(PROFILE["skills"])
    roles_str   = ", ".join(PROFILE["target_roles"])
    sectors_str = ", ".join(PROFILE["sectors"])

    linkedin_instruction = ""
    if include_linkedin:
        linkedin_instruction = """
LINKEDIN POST (include this month only):
Draft a LinkedIn post for a Tech Lead AVP in Dubai fintech.
The post should:
- Be based on a trend or insight you observed in the market this week
- Sound like a real senior engineer — direct, practical, no corporate fluff
- Be 150-200 words
- End with a question to drive comments
- Include 4-5 relevant hashtags
- NOT sound like AI wrote it
- Reference something specific and real from the market data above

Include in your JSON response:
"linkedin_post": {{
  "suggested_angle": "one line describing the post angle",
  "draft": "the full post text ready to copy-paste",
  "hashtags": ["#tag1", "#tag2"]
}}
"""

    prompt = f"""You are a career intelligence analyst for a senior software engineer in Dubai.
Today is {today} (Week: {week_range}).

ENGINEER PROFILE:
- Title: {PROFILE['current_title']} at {PROFILE['current_company']}
- Skills: {skills_str}
- Target roles: {roles_str}
- Domain: {PROFILE['domain']}
- Location: {PROFILE['location']}
- Min salary expectation: AED {PROFILE['min_salary_aed']:,}/month
- Sectors of interest: {sectors_str}

YOUR TASK:
Use web search to research the Dubai and UAE tech/fintech job market this week. Search for:
1. Senior engineering roles in Dubai fintech matching the profile above
2. Skill trends appearing in senior engineering JDs in UAE/Dubai
3. Salary data for Principal Engineer / Tech Lead roles in Dubai
4. News about which fintech/tech companies in UAE are hiring, expanding, or recently funded
5. Any major tech/AI trends relevant to a Java/Kafka/microservices engineer
6. Discover which companies in UAE fintech/tech are currently most active in senior hiring
   — do NOT rely on a fixed list, find what is actually happening in the market this week

{linkedin_instruction}

Produce a JSON response with this exact structure:
{{
  "week": "{week_range}",
  "date": "{today}",
  "market_pulse": "one sentence summary of Dubai tech hiring market this week",
  "matching_roles": [
    {{
      "title": "exact job title",
      "company": "company name",
      "salary_range": "AED X-Y/month or Not disclosed",
      "match_score": "High / Medium",
      "match_reasons": ["reason 1", "reason 2"],
      "location": "Dubai / Remote / Hybrid",
      "source": "LinkedIn / Bayt / Company site"
    }}
  ],
  "skill_trends": {{
    "rising": ["skill 1", "skill 2"],
    "stable": ["skill 1", "skill 2"],
    "fading": ["skill 1", "skill 2"],
    "insight": "one sentence insight on what this means for the engineer"
  }},
  "salary_benchmark": {{
    "principal_engineer": "AED X-Y/month",
    "tech_lead_avp": "AED X-Y/month",
    "staff_engineer": "AED X-Y/month",
    "trend": "Stable / Rising / Falling",
    "note": "any context on salary trends"
  }},
  "companies_to_watch": [
    {{
      "company": "company name — discovered from live market search, not a fixed list",
      "reason": "specific reason why they are worth watching THIS week — be concrete",
      "signal": "Hiring / Expanding / Funding / Restructuring",
      "roles_posted": "number of relevant senior roles posted recently or Unknown"
    }}
  ],
  "weekly_insight": "2-3 sentences of career advice or market observation specifically for this engineer this week",
  "linkedin_post": null
}}

If include_linkedin is false, set linkedin_post to null.
Respond ONLY with the JSON object, no preamble or markdown."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract text
    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    print("  ✓ Claude response received")

    # Parse JSON
    try:
        start = full_text.find("{")
        end   = full_text.rfind("}") + 1
        if start != -1 and end > start:
            result = json.loads(full_text[start:end])
            print(f"  ✓ Analysis parsed: {result.get('market_pulse', 'N/A')[:60]}...")
            return result
    except Exception as e:
        print(f"  ✗ JSON parse error: {e}")

    # Fallback
    return {
        "week":             week_range,
        "date":             str(today),
        "market_pulse":     "Data unavailable this week.",
        "matching_roles":   [],
        "skill_trends":     {"rising": [], "stable": [], "fading": [], "insight": ""},
        "salary_benchmark": {"principal_engineer": "N/A", "tech_lead_avp": "N/A",
                             "staff_engineer": "N/A", "trend": "N/A", "note": ""},
        "companies_to_watch": [],
        "weekly_insight":   "Agent encountered an error. Please check logs.",
        "linkedin_post":    None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# EMAIL BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_email_html(data: dict, include_linkedin: bool) -> str:
    """Build the career intelligence HTML email."""

    week           = data.get("week", "")
    market_pulse   = data.get("market_pulse", "")
    roles          = data.get("matching_roles", [])
    skill_trends   = data.get("skill_trends", {})
    salary         = data.get("salary_benchmark", {})
    companies      = data.get("companies_to_watch", [])
    weekly_insight = data.get("weekly_insight", "")
    linkedin       = data.get("linkedin_post")

    # ── Matching roles
    role_rows = ""
    for role in roles[:5]:  # max 5 roles
        score       = role.get("match_score", "Medium")
        score_color = "#16a34a" if score == "High" else "#ca8a04"
        score_bg    = "#dcfce7" if score == "High" else "#fef9c3"
        reasons     = " · ".join(role.get("match_reasons", []))
        role_rows += f"""
        <tr>
          <td style="padding:12px;border-bottom:1px solid #f3f4f6;">
            <div style="font-weight:700;color:#111827;font-size:14px;">
              {role.get('title', '')}
            </div>
            <div style="color:#6b7280;font-size:12px;margin-top:2px;">
              {role.get('company', '')} · {role.get('location', '')}
            </div>
            <div style="color:#9ca3af;font-size:11px;margin-top:4px;">{reasons}</div>
          </td>
          <td style="padding:12px;border-bottom:1px solid #f3f4f6;text-align:center;
                     white-space:nowrap;">
            <span style="background:{score_bg};color:{score_color};padding:3px 10px;
                         border-radius:5px;font-weight:700;font-size:12px;">{score} Match</span>
          </td>
          <td style="padding:12px;border-bottom:1px solid #f3f4f6;color:#374151;
                     font-size:13px;font-weight:600;white-space:nowrap;">
            {role.get('salary_range', 'N/A')}
          </td>
          <td style="padding:12px;border-bottom:1px solid #f3f4f6;color:#9ca3af;font-size:11px;">
            {role.get('source', '')}
          </td>
        </tr>"""

    if not role_rows:
        role_rows = """<tr><td colspan="4" style="padding:16px;text-align:center;
                       color:#9ca3af;font-size:13px;">No strong matching roles found this week.</td></tr>"""

    # ── Skill tags helper
    def skill_tags(skills, color, bg):
        return "".join(
            f'<span style="background:{bg};color:{color};padding:3px 10px;border-radius:12px;'
            f'font-size:12px;font-weight:600;margin:3px 3px 3px 0;display:inline-block;">{s}</span>'
            for s in skills
        )

    rising_tags = skill_tags(skill_trends.get("rising", []), "#16a34a", "#dcfce7")
    stable_tags = skill_tags(skill_trends.get("stable", []), "#2563eb", "#dbeafe")
    fading_tags = skill_tags(skill_trends.get("fading", []), "#9ca3af", "#f3f4f6")

    # ── Companies to watch
    company_rows = ""
    signal_colors = {
        "Hiring":       ("#16a34a", "#dcfce7"),
        "Expanding":    ("#2563eb", "#dbeafe"),
        "Funding":      ("#7c3aed", "#ede9fe"),
        "Restructuring":("#dc2626", "#fee2e2"),
    }
    for co in companies[:5]:
        signal       = co.get("signal", "Hiring")
        sc, sb       = signal_colors.get(signal, ("#6b7280", "#f3f4f6"))
        roles_posted = co.get("roles_posted", "")
        roles_note   = f" &nbsp;<span style='color:#9ca3af;font-weight:400;font-size:11px;'>{roles_posted} roles posted</span>" if roles_posted and roles_posted != "Unknown" else ""
        company_rows += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;font-weight:600;
                     color:#111827;font-size:13px;">{co.get('company', '')}{roles_note}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;">
            <span style="background:{sb};color:{sc};padding:2px 8px;border-radius:4px;
                         font-size:11px;font-weight:700;">{signal}</span>
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #f3f4f6;color:#6b7280;
                     font-size:12px;">{co.get('reason', '')}</td>
        </tr>"""

    if not company_rows:
        company_rows = """<tr><td colspan="3" style="padding:16px;text-align:center;
                          color:#9ca3af;font-size:13px;">No notable signals this week.</td></tr>"""

    # ── LinkedIn section (only on first Monday of month)
    linkedin_section = ""
    if include_linkedin and linkedin:
        draft    = linkedin.get("draft", "").replace("\n", "<br>")
        angle    = linkedin.get("suggested_angle", "")
        hashtags = " ".join(linkedin.get("hashtags", []))
        linkedin_section = f"""
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;background:#fafaf9;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:6px;">✍️ Monthly LinkedIn Draft</div>
      <div style="color:#6b7280;font-size:12px;margin-bottom:14px;">
        Suggested angle: <em>{angle}</em>
      </div>
      <div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;
                  padding:16px 20px;font-size:13px;color:#374151;line-height:1.8;">
        {draft}
      </div>
      <div style="margin-top:10px;color:#9ca3af;font-size:12px;">
        {hashtags}
      </div>
      <div style="margin-top:10px;color:#9ca3af;font-size:11px;">
        ↑ Review, personalise with one specific real detail, then post.
      </div>
    </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">

  <div style="max-width:700px;margin:32px auto;background:#ffffff;border-radius:12px;
               overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e1b4b 0%,#4f46e5 100%);padding:28px 32px;">
      <div style="color:#a5b4fc;font-size:12px;font-weight:600;letter-spacing:1px;
                  text-transform:uppercase;">Career Intelligence Agent</div>
      <div style="color:#ffffff;font-size:22px;font-weight:700;margin-top:4px;">
        Weekly Brief · {week}
      </div>
      <div style="color:#c7d2fe;font-size:14px;margin-top:8px;line-height:1.6;">
        {market_pulse}
      </div>
    </div>

    <!-- Matching Roles -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:12px;">👔 Roles Matching Your Profile</div>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Role</th>
            <th style="padding:8px 12px;text-align:center;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Match</th>
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Salary</th>
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Source</th>
          </tr>
        </thead>
        <tbody>{role_rows}</tbody>
      </table>
    </div>

    <!-- Skill Trends -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:14px;">📈 Skill Trends This Week</div>
      <div style="margin-bottom:10px;">
        <span style="font-size:11px;font-weight:700;color:#6b7280;
                     text-transform:uppercase;">Rising &nbsp;</span>
        {rising_tags if rising_tags else '<span style="color:#9ca3af;font-size:12px;">None notable</span>'}
      </div>
      <div style="margin-bottom:10px;">
        <span style="font-size:11px;font-weight:700;color:#6b7280;
                     text-transform:uppercase;">Stable &nbsp;</span>
        {stable_tags if stable_tags else '<span style="color:#9ca3af;font-size:12px;">N/A</span>'}
      </div>
      <div style="margin-bottom:14px;">
        <span style="font-size:11px;font-weight:700;color:#6b7280;
                     text-transform:uppercase;">Fading &nbsp;</span>
        {fading_tags if fading_tags else '<span style="color:#9ca3af;font-size:12px;">None notable</span>'}
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
                     border-bottom:1px solid #f3f4f6;">{salary.get('principal_engineer', 'N/A')}</td>
        </tr>
        <tr>
          <td style="padding:10px 14px;font-size:13px;color:#374151;font-weight:600;
                     border-bottom:1px solid #f3f4f6;">Tech Lead AVP</td>
          <td style="padding:10px 14px;font-size:13px;color:#111827;font-weight:700;
                     border-bottom:1px solid #f3f4f6;">{salary.get('tech_lead_avp', 'N/A')}</td>
        </tr>
        <tr style="background:#f9fafb;">
          <td style="padding:10px 14px;font-size:13px;color:#374151;font-weight:600;">
            Staff Engineer</td>
          <td style="padding:10px 14px;font-size:13px;color:#111827;font-weight:700;">
            {salary.get('staff_engineer', 'N/A')}</td>
        </tr>
      </table>
      <div style="margin-top:10px;color:#6b7280;font-size:12px;">
        Trend: <strong>{salary.get('trend', 'N/A')}</strong> · {salary.get('note', '')}
      </div>
    </div>

    <!-- Companies to Watch -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:12px;">🔍 Companies to Watch</div>
      <table style="width:100%;border-collapse:collapse;">
        <thead>
          <tr style="background:#f9fafb;">
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Company</th>
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Signal</th>
            <th style="padding:8px 12px;text-align:left;font-size:11px;color:#6b7280;
                       font-weight:600;text-transform:uppercase;">Why</th>
          </tr>
        </thead>
        <tbody>{company_rows}</tbody>
      </table>
    </div>

    <!-- Weekly Insight -->
    <div style="padding:24px 32px;border-bottom:1px solid #e5e7eb;background:#f8faff;">
      <div style="font-size:13px;font-weight:700;color:#6b7280;letter-spacing:0.5px;
                  text-transform:uppercase;margin-bottom:10px;">🧠 This Week's Insight</div>
      <p style="margin:0;color:#1e1b4b;font-size:14px;line-height:1.7;font-weight:500;">
        {weekly_insight}
      </p>
    </div>

    {linkedin_section}

    <!-- Footer -->
    <div style="padding:16px 32px;background:#f9fafb;">
      <p style="margin:0;font-size:11px;color:#9ca3af;text-align:center;">
        Career Intelligence Agent · Runs every Friday 07:00 UAE time<br>
        LinkedIn draft included on first Monday of each month
      </p>
    </div>

  </div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL LOG
# ─────────────────────────────────────────────────────────────────────────────

def append_career_log(data: dict, include_linkedin: bool) -> None:
    """Appends weekly summary to career_log.csv for tracking over time."""
    headers = [
        "date", "week", "roles_found", "high_match_roles",
        "top_rising_skill", "salary_trend", "linkedin_drafted", "market_pulse"
    ]

    roles          = data.get("matching_roles", [])
    high_match     = sum(1 for r in roles if r.get("match_score") == "High")
    rising_skills  = data.get("skill_trends", {}).get("rising", [])
    top_skill      = rising_skills[0] if rising_skills else ""

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
            print(f"  ✓ Created new career log: {LOG_FILE}")

        writer.writerow({
            "date":             data.get("date", ""),
            "week":             data.get("week", ""),
            "roles_found":      len(roles),
            "high_match_roles": high_match,
            "top_rising_skill": top_skill,
            "salary_trend":     data.get("salary_benchmark", {}).get("trend", ""),
            "linkedin_drafted": include_linkedin,
            "market_pulse":     data.get("market_pulse", "")[:100],
        })

    print(f"  ✓ Career log updated for {data.get('date', '')}")


# ─────────────────────────────────────────────────────────────────────────────
# SEND EMAIL
# ─────────────────────────────────────────────────────────────────────────────

def send_email(html: str, data: dict, include_linkedin: bool) -> None:
    sender    = os.environ["EMAIL_ADDRESS"]
    password  = os.environ["EMAIL_PASSWORD"]
    recipient = os.environ.get("TO_EMAIL", sender)

    week       = data.get("week", "")
    roles      = data.get("matching_roles", [])
    high_match = sum(1 for r in roles if r.get("match_score") == "High")

    linkedin_tag = " · 📝 LinkedIn Draft Ready" if include_linkedin else ""
    subject = f"👔 Career Brief · {week} · {high_match} High Match Role{'s' if high_match != 1 else ''}{linkedin_tag}"

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
    print(f"  Career Intelligence Agent · {today}")
    print(f"{'─'*60}\n")

    include_linkedin = is_first_monday_of_month(today)
    print(f"[ CONFIG ] Week: {get_week_range(today)}")
    print(f"[ CONFIG ] Include LinkedIn draft: {include_linkedin}")
    print()

    # 1. Claude analysis with web search
    print("[ LAYER 1 ] Running career market analysis...")
    data = call_career_agent(include_linkedin)
    print()

    # 2. Build and send email
    print("[ LAYER 2 ] Building and sending email...")
    html = build_email_html(data, include_linkedin)
    send_email(html, data, include_linkedin)
    print()

    # 3. Log to CSV
    print("[ LAYER 3 ] Logging to career_log.csv...")
    append_career_log(data, include_linkedin)

    print(f"\n{'─'*60}")
    print(f"  Agent complete · {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{'─'*60}\n")


if __name__ == "__main__":
    main()
