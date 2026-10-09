# Katha Reels – Audio se cartoon animation (free)

Aap `audio/` folder mein katha ki audio daalo. Roz subah apne aap 9:16 cartoon video ban jaayegi:
naye characters, background, aur shabd-dar-shabd Hindi subtitles ke saath.

## Ek baar ka setup (10 minute)

1. **Gemini free key lo**
   - https://aistudio.google.com/apikey kholo, Google account se login karo.
   - **Create API key** dabao aur key copy karo.

2. **GitHub repo banao** (Private bhi chalega) aur is zip ki saari files upload karo:
   - Repo mein **Add file → Upload files** dabao.
   - Zip ke andar ka pura saman (`src/`, `audio/`, `.github/`, `requirements.txt`, `README.md`, `.gitignore`) drag karo.
   - ⚠️ `.github` folder chhupa (hidden) ho sakta hai. Upload ke baad repo mein `.github/workflows/daily.yml` dikhna chahiye. Na dikhe to **Add file → Create new file** se naam `.github/workflows/daily.yml` likho aur us file ka content paste karo.

3. **Key repo mein daalo**
   - Repo → **Settings → Secrets and variables → Actions → New repository secret**.
   - Name: `GEMINI_API_KEY`, Value: apni key → **Add secret**.

4. **Permission do**
   - **Settings → Actions → General → Workflow permissions** mein **Read and write permissions** chuno → Save.

## Roz ka kaam

1. `audio/` folder mein audio upload karo (mp3/m4a/wav). Naam aise rakho: `01_bhola_khichdi.mp3`, `02_...`. Har din ek file, number ke kram se.
2. Subah 8:52 par video apne aap banegi. Abhi chahiye to: **Actions → Daily Katha Reel → Run workflow**.
3. Video lene ke liye: **Actions** → upar wala hara ✅ run → neeche **Artifacts** → `katha-reel-…` download (zip ke andar mp4).
4. Ek video banne mein lagbhag 10–20 minute lagte hain (70 sec audio ke liye).

## Settings (`.github/workflows/daily.yml` mein)

| Setting | Matlab |
|---|---|
| `WHISPER_MODEL: large-v3-turbo` | Hindi samajhne wala model. Run dheema lage to `small` likho (spelling Gemini phir bhi sudhaarega) |
| `GEMINI_MODEL` | Khaali chhodo, code khud model chunta hai. Koi khaas model chahiye to uska naam likho |
| `FPS: "24"` | Smoothness. `30` = zyada smooth, render dheema |
| `cron` | Roz ka time (UTC mein). `22 3 * * *` = 8:52 IST |

## Kuch gadbad ho to

- **Run laal ❌ ho gaya:** us run par click karke "Video banao" step kholo, aakhri lines dekho.
- **"GEMINI_API_KEY nahi mila":** step 3 dobara karo.
- **Background saade rang ke aaye:** Pollinations us din busy tha, code ne backup background laga diya. Agle din theek ho jaata hai.
- **Koi character saada "aadmi" jaisa aaya:** Gemini ka SVG kharab tha, backup laga. Workflow dobara chalao.
- `work/<naam>/plan.json` (artifact mein) dikhata hai ki AI ne kaun se scene socha.
