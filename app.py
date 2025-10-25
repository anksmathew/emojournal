import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import streamlit as st

DATA_FILE = Path("journal_data.json")

st.set_page_config(page_title="Dynamic Emotion-Aware Journal", layout="wide")


def load_data() -> Dict[str, dict]:
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def save_data(data: Dict[str, dict]) -> None:
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def initialize_day(data: Dict[str, dict], day_key: str) -> Dict[str, dict]:
    entry = data.setdefault(day_key, {})
    entry.setdefault("checkin", {})
    entry.setdefault("prompts", [])
    entry.setdefault("responses", [])
    entry.setdefault("reflection", {})
    entry.setdefault("tags", [])
    return entry


PROMPT_BANK = {
    "happy": [
        "What is amplifying your happiness today?",
        "How can you share this joy with someone else?",
        "What meaningful goal could you stretch toward while feeling uplifted?",
        "Which moment today feels worth savoring twice?",
        "How can you anchor this positive energy for later in the week?",
        "What personal strength is shining right now?",
        "Where can you invest your good mood for long-term payoff?",
    ],
    "calm": [
        "What is contributing to your sense of calm today?",
        "Which gentle challenge could you welcome while grounded?",
        "How can you create a meaningful pause in your day?",
        "Where do you feel most at ease right now?",
        "What intention will help you stay centered?",
        "How might you extend this calm to someone else?",
    ],
    "grateful": [
        "Who or what are you thankful for this morning?",
        "What recent act of kindness are you still thinking about?",
        "How can you express gratitude through action today?",
        "Which small detail is quietly bringing you joy?",
        "How is gratitude shaping your outlook right now?",
        "Where could you pay forward something you appreciate?",
    ],
    "productive": [
        "What momentum are you bringing into today?",
        "Which priority will feel most satisfying to complete?",
        "How can you elevate one task from good to great?",
        "What will progress look like by the end of the day?",
        "How can you balance effort with restoration?",
        "What collaboration could amplify your productivity?",
    ],
    "anxious": [
        "What is the worry saying, and what calmer voice can respond?",
        "Which steady breath or grounding ritual can help right now?",
        "What is one manageable step you can take despite the nerves?",
        "Who could you reach out to for reassurance or perspective?",
        "What evidence do you have that you can handle this?",
        "How might you gently reframe the story your mind is telling?",
    ],
    "stressed": [
        "What is the biggest weight on your mind and why?",
        "Which task can you simplify or delegate today?",
        "What boundary would lighten your load?",
        "Who could support you if you asked?",
        "What would feeling supported look like right now?",
        "Which calming practice can help you reset between tasks?",
    ],
    "sad": [
        "What emotion sits beneath the sadness today?",
        "Which comforting memory or activity could you revisit?",
        "Who could you lean on for connection right now?",
        "What small act of kindness can you offer yourself?",
        "How can you honor this feeling without letting it define the day?",
        "Where is a glimmer of hope, however small?",
    ],
    "tired": [
        "What is draining your energy most today?",
        "Which commitments could be softened or postponed?",
        "How can you carve out a brief moment of restoration?",
        "Who could lend a hand so you can rest?",
        "What signals from your body are asking to be heard?",
        "Where might you find a gentle boost without overextending?",
    ],
    "angry": [
        "What boundary feels crossed and how can you address it?",
        "Which physical outlet could help release tension safely?",
        "What part of this situation is within your control?",
        "Who can help you process this feeling productively?",
        "How might you transform this energy into constructive action?",
        "What would compassion toward yourself look like right now?",
    ],
    "overwhelmed": [
        "Which obligation feels loudest and why?",
        "What is one tiny step that would create a sense of progress?",
        "Who could you ask for a reality check or support?",
        "Where can you introduce breathing room in your schedule?",
        "How can you break your focus into doable segments?",
        "What would it mean to be gentle with yourself today?",
    ],
    "apathetic": [
        "What might spark even a small sense of curiosity today?",
        "Which value of yours could use a little attention?",
        "Who could help you reconnect with meaning right now?",
        "What simple routine could add momentum to your morning?",
        "How could you experiment with a tiny change in your day?",
        "What would make today feel 1% better?",
    ],
}

GRATITUDE_PROMPTS = [
    "Name something fresh you’re grateful for this morning.",
    "Who made a positive difference yesterday, and how will you thank them?",
    "What everyday privilege or comfort deserves your gratitude today?",
]

MICRO_ACTION_PROMPTS = [
    "What micro-action will you take in the next hour to support yourself?",
    "Identify one 5-minute task that nudges you forward—what is it?",
    "What is a tiny commitment you can make before midday?",
]

GENERIC_PROMPTS = [
    "Which part of your day could use extra compassion?",
    "What story are you telling yourself, and how could you rewrite it?",
    "Where can you invite more presence into your routine today?",
    "What would make today feel meaningful when you look back tonight?",
    "How will you know you honored your needs by day’s end?",
]

POSITIVE_EMOTIONS = {"happy", "calm", "grateful", "productive"}
NEGATIVE_EMOTIONS = {
    "anxious",
    "stressed",
    "sad",
    "tired",
    "angry",
    "overwhelmed",
    "apathetic",
}


def get_recent_prompts(data: Dict[str, dict], today_key: str, lookback: int = 3) -> List[str]:
    cutoff_dates = []
    try:
        today_dt = datetime.fromisoformat(today_key)
    except ValueError:
        today_dt = datetime.combine(date.today(), datetime.min.time())
    for i in range(1, lookback + 1):
        prev_day = today_dt - timedelta(days=i)
        key = prev_day.date().isoformat()
        if key in data:
            cutoff_dates.append(key)
    recent = []
    for key in cutoff_dates:
        recent.extend(data[key].get("prompts", []))
    return recent


def choose_prompt(options: List[str], excluded: set) -> str:
    filtered = [p for p in options if p not in excluded]
    if filtered:
        return random.choice(filtered)
    return random.choice(options)


def generate_prompts(emotion: str, data: Dict[str, dict], today_key: str) -> List[str]:
    recent_prompts = set(get_recent_prompts(data, today_key))
    base_prompts = PROMPT_BANK.get(emotion, []) + GENERIC_PROMPTS

    selected = []
    excluded = set(recent_prompts)

    gratitude_prompt = choose_prompt(GRATITUDE_PROMPTS, excluded)
    selected.append(gratitude_prompt)
    excluded.add(gratitude_prompt)

    micro_prompt = choose_prompt(MICRO_ACTION_PROMPTS, excluded)
    selected.append(micro_prompt)
    excluded.add(micro_prompt)

    desired_total = random.randint(3, 5)
    random.shuffle(base_prompts)

    if emotion in POSITIVE_EMOTIONS:
        # Encourage savoring and stretching
        base_prompts.extend([
            "Where can you stretch today without losing joy?",
            "What meaning can you draw from the good surrounding you?",
        ])
    elif emotion in NEGATIVE_EMOTIONS:
        base_prompts.extend([
            "What grounding ritual can you lean on in the next hour?",
            "Who could you ask for a small boost or check-in?",
            "Identify one small win you can create before evening.",
        ])

    for prompt in base_prompts:
        if len(selected) >= desired_total:
            break
        if prompt in excluded:
            continue
        selected.append(prompt)
        excluded.add(prompt)

    # If we still need more prompts, allow repeats beyond exclusion
    while len(selected) < desired_total and base_prompts:
        candidate = random.choice(base_prompts)
        if candidate not in selected:
            selected.append(candidate)
        else:
            break

    return selected


def render_header(today_key: str) -> None:
    st.title("Dynamic Emotion-Aware Journal")
    st.subheader(date.fromisoformat(today_key).strftime("%A, %B %d, %Y"))
    st.write("---")


def display_prompt_history(data: Dict[str, dict], today_key: str) -> None:
    with st.expander("Prompt history", expanded=False):
        if not data:
            st.info("No prompt history yet. Your reflections will appear here.")
            return
        sorted_days = sorted(data.keys(), reverse=True)
        for day in sorted_days:
            if day == today_key:
                continue
            entry = data.get(day, {})
            prompts = entry.get("prompts", [])
            if not prompts:
                continue
            st.markdown(f"**{datetime.fromisoformat(day).strftime('%b %d, %Y')}**")
            for prompt in prompts:
                st.markdown(f"- {prompt}")
            st.write("")


def responses_form(day_entry: Dict[str, dict], day_key: str, data: Dict[str, dict]) -> None:
    prompts = day_entry.get("prompts", [])
    if not prompts:
        return

    st.markdown("### Journal prompts")
    with st.form("prompt_responses"):
        responses = []
        for idx, prompt in enumerate(prompts):
            default_text = ""
            saved_responses = day_entry.get("responses", [])
            if idx < len(saved_responses):
                default_text = saved_responses[idx]
            responses.append(
                st.text_area(prompt, value=default_text, key=f"response_{idx}")
            )
        submit = st.form_submit_button("Save responses")
    if submit:
        day_entry["responses"] = responses
        data[day_key] = day_entry
        save_data(data)
        st.success("Responses saved.")



def tags_section(day_entry: Dict[str, dict], day_key: str, data: Dict[str, dict]) -> None:
    st.markdown("### Tags")
    existing_tags = ", ".join(day_entry.get("tags", []))
    with st.form("tag_form"):
        tag_input = st.text_input(
            "Add tags (comma-separated)", value=existing_tags, help="Use tags to spot patterns."
        )
        submit = st.form_submit_button("Save tags")
    if submit:
        tags = [tag.strip() for tag in tag_input.split(",") if tag.strip()]
        day_entry["tags"] = tags
        data[day_key] = day_entry
        save_data(data)
        st.success("Tags updated.")


def reflection_form(day_entry: Dict[str, dict], day_key: str, data: Dict[str, dict]) -> None:
    if not day_entry.get("checkin"):
        st.info("Complete your daily check-in to unlock the evening reflection.")
        return

    st.write("---")
    st.markdown("## End-of-day reflection")

    reflection = day_entry.get("reflection", {})

    with st.form("reflection_form"):
        highlight = st.text_area("Highlight of the day", value=reflection.get("highlight", ""))
        lesson = st.text_area("Lesson or insight", value=reflection.get("lesson", ""))
        gratitude = st.text_area("Evening gratitude", value=reflection.get("gratitude", ""))
        one_word = st.text_input("One word to describe the day", value=reflection.get("one_word", ""))
        sleep_target = st.text_input(
            "Sleep intention or target (optional)", value=reflection.get("sleep_target", "")
        )
        submitted = st.form_submit_button("Save reflection")

    if submitted:
        day_entry["reflection"] = {
            "highlight": highlight,
            "lesson": lesson,
            "gratitude": gratitude,
            "one_word": one_word,
            "sleep_target": sleep_target,
        }
        data[day_key] = day_entry
        save_data(data)
        st.success("Reflection saved.")


def compute_dashboard(data: Dict[str, dict], today_key: str) -> None:
    st.write("---")
    st.markdown("## 7-day dashboard")
    if not data:
        st.info("Your dashboard will appear after you log entries.")
        return

    today_dt = datetime.fromisoformat(today_key)
    last_week_keys = []
    for i in range(6, -1, -1):
        day_key = (today_dt - timedelta(days=i)).date().isoformat()
        if day_key in data:
            last_week_keys.append(day_key)

    if not last_week_keys:
        st.info("No entries from the past week yet.")
        return

    records = []
    emotion_counts = {}
    word_counts = []

    for key in last_week_keys:
        entry = data.get(key, {})
        checkin = entry.get("checkin", {})
        emotion = checkin.get("emotion")
        energy = checkin.get("energy")
        if energy is not None:
            records.append({"date": key, "energy": energy})
        if emotion:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Word count from responses and reflection
        words = 0
        for response in entry.get("responses", []):
            words += len(response.split())
        for value in entry.get("reflection", {}).values():
            if value:
                words += len(value.split())
        word_counts.append({"date": key, "words": words})

    dashboard_cols = st.columns(3)
    with dashboard_cols[0]:
        if records:
            df_energy = pd.DataFrame(records)
            df_energy.sort_values("date", inplace=True)
            df_energy.set_index("date", inplace=True)
            st.markdown("**Energy trend**")
            st.line_chart(df_energy)
        else:
            st.info("Energy trend will appear after recording energy levels.")

    with dashboard_cols[1]:
        if emotion_counts:
            df_emotion = pd.DataFrame(
                {"emotion": list(emotion_counts.keys()), "count": list(emotion_counts.values())}
            )
            df_emotion.set_index("emotion", inplace=True)
            st.markdown("**Emotion frequency**")
            st.bar_chart(df_emotion)
        else:
            st.info("Emotion frequency will appear after logging emotions.")

    with dashboard_cols[2]:
        if word_counts:
            df_words = pd.DataFrame(word_counts)
            df_words.sort_values("date", inplace=True)
            df_words.set_index("date", inplace=True)
            st.markdown("**Word count per day**")
            st.bar_chart(df_words)
        else:
            st.info("Word count appears after writing responses.")


def main():
    data = load_data()
    today_key = date.today().isoformat()
    day_entry = initialize_day(data, today_key)

    render_header(today_key)

    st.markdown("## Daily check-in")
    checkin = day_entry.get("checkin", {})

    with st.form("daily_checkin"):
        emotion = st.selectbox(
            "How are you arriving today?",
            options=list(PROMPT_BANK.keys()),
            index=list(PROMPT_BANK.keys()).index(checkin.get("emotion", "happy"))
            if checkin.get("emotion") in PROMPT_BANK
            else 0,
        )
        energy = st.slider("Energy level", min_value=1, max_value=10, value=checkin.get("energy", 5))
        focus = st.text_input(
            "What are you aiming for today? (optional)", value=checkin.get("focus", "")
        )
        submitted = st.form_submit_button("Save check-in & refresh prompts")

    if submitted:
        day_entry["checkin"] = {"emotion": emotion, "energy": energy, "focus": focus}
        prior_prompts = day_entry.get("prompts", [])
        prior_responses = day_entry.get("responses", [])
        new_prompts = generate_prompts(emotion, data, today_key)

        new_responses = []
        for prompt in new_prompts:
            if prompt in prior_prompts:
                idx = prior_prompts.index(prompt)
                if idx < len(prior_responses):
                    new_responses.append(prior_responses[idx])
                    continue
            new_responses.append("")

        day_entry["prompts"] = new_prompts
        day_entry["responses"] = new_responses
        data[today_key] = day_entry
        save_data(data)
        st.success("Check-in saved and prompts refreshed.")

    responses_form(day_entry, today_key, data)
    tags_section(day_entry, today_key, data)
    reflection_form(day_entry, today_key, data)
    compute_dashboard(data, today_key)
    display_prompt_history(data, today_key)


if __name__ == "__main__":
    main()
