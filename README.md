# Mackney Gazette

Generates a fictional local newspaper for a made-up English town. It builds the town and its residents from scratch, then uses an LLM to write articles in the voice of different journalists. Stories can continue across multiple articles.

There's a sample town (Mackney) and a couple of articles in `sample_data/` if you want to see what the output looks like before running anything.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need a Gemini API key (free tier works — get one at [aistudio.google.com](https://aistudio.google.com)):

```bash
export GEMINI_API_KEY=your_key_here
```

To use a different model, set `LITELLM_MODEL` — it routes through [LiteLLM](https://github.com/BerriAI/litellm) so anything supported there works:

```bash
export LITELLM_MODEL=gpt-4o-mini  # needs OPENAI_API_KEY instead
```

## Running it

**First time — generate the town and its residents:**
```bash
./initialise_town.sh
```
This writes `data/town_data.json` and `data/people_data.csv`. You only need to do this once.

**Generate articles:**
```bash
./generate_articles_daily.sh
```
Appends new articles to `data/articles.csv`. Run it daily (or automate it — there's a cron example in `articles_daily_config.yaml`).

**View in a browser:**
```bash
pip install -r app/requirements.txt
FLASK_APP=app/app.py flask run --port=5001
```
Open `http://localhost:5001`.

## Configuration

`town_init_config.yaml` controls the town name, locale, seed, and population size.

`articles_daily_config.yaml` controls how many articles to generate per run, the ratio of new stories to continuations, tone distribution, and article retention limits.

Both files have inline comments explaining each option.

## Structure

```
src/                   generation engine
app/                   local Flask UI
sample_data/           example output (town, people, articles)
data/                  your generated data (gitignored)
```
