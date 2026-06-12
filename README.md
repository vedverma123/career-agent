# career-agent

> AI agent that monitors the Dubai fintech job market weekly and delivers a career intelligence brief every Friday — roles matching your profile, skill trends, salary benchmarks, companies to watch, and a monthly LinkedIn post draft.

## What it does

**Every Friday — Weekly Career Brief:**
- 👔 Roles matching your profile (Principal Engineer / Tech Lead in Dubai fintech)
- 📈 Skill trends — rising, stable, fading in senior engineering JDs
- 💰 Salary benchmarks — current market rates for your level in Dubai
- 🧠 Weekly insight — one actionable career observation

**First Monday of each month — adds:**
- ✍️ LinkedIn post draft — ready to review, personalise, and post

---

## Setup (10 minutes)

### 1. Create a private GitHub repo named `career-agent`

```bash
git init career-agent
cd career-agent
# copy all files maintaining folder structure
git add .
git commit -m "Initial career agent setup"
git remote add origin https://github.com/YOUR_USERNAME/career-agent.git
git push -u origin main
```

### 2. Add GitHub Secrets

Go to repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `EMAIL_ADDRESS` | Your Gmail address |
| `EMAIL_PASSWORD` | Gmail app password (16 chars) |
| `TO_EMAIL` | Where to receive the brief |

### 3. Test it

**Actions → Career Intelligence Agent → Run workflow**

---

## Schedule

| Trigger | Day | Time (UAE) | What runs |
|---------|-----|------------|-----------|
| Scheduled | Every Friday | 08:00 | Full weekly brief |
| Scheduled | Every Monday | 08:00 | LinkedIn draft check (only sends on 1st Monday of month) |
| Manual | Any time | On demand | Full run |

---

## File structure

```
career-agent/
├── career_agent.py              # Main agent
├── requirements.txt             # Dependencies (anthropic only)
├── career_log.csv               # Auto-generated signal history
├── README.md                    # This file
└── .github/
    └── workflows/
        └── career_agent.yml     # Scheduler
```

---

## Cost

| Item | Cost |
|------|------|
| GitHub Actions | Free |
| Anthropic API | ~$0.20–0.30/week (~$1/month) |
| Gmail SMTP | Free |

---

## Customising your profile

Edit the `PROFILE` dictionary at the top of `career_agent.py`:

```python
PROFILE = {
    "current_title":   "Tech Lead AVP",
    "skills":          ["Java", "Spring Boot", "Kafka", ...],
    "target_roles":    ["Principal Engineer", ...],
}
```

---

*Career intelligence tool — not a recruitment service. Always verify roles directly on source platforms.*
