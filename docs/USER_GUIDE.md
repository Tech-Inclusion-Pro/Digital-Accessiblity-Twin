# AccessTwin User Guide

AccessTwin helps students with accommodations document what works for them,
and helps teachers plan supports — without the student's personal
information ever leaving their hands unless they choose to share it.

Everything runs locally: data is stored encrypted on your own device, and
AI features default to local models (Ollama, LM Studio, GPT4All). No
account with any online service is required.

---

## Getting Started

**Running the app**
- Packaged app: open **AccessTwin** from Applications.
- From source: `python main.py` in the project folder
  (requires Python 3.10+ and `pip install -r requirements.txt`).

**AI features** (insights, coach, privacy check) need a local AI backend.
The default is [Ollama](https://ollama.com) with the `gemma3:4b` model:

```bash
ollama pull gemma3:4b
```

Configure or change backends any time under **AI Settings** in the sidebar.

**Creating an account** — on the login screen, open the **Register** tab,
choose your role (**Student** or **Teacher**), and set a username, password,
and security questions. An accessibility toolbar (text size, contrast,
spacing, and more) is available before you even log in.

---

## For Students

Your **accessibility twin** is your own record of what helps you learn.
You build it over time from the sidebar:

1. **My Profile** — your strengths, supports, history, hopes and goals,
   and the people who support you (stakeholders). This is the private
   core of your twin; most of it never leaves your device.
2. **Log Experience** — record supports as you try them: what it is,
   the category, and an effectiveness rating from 1–5. These ratings
   later drive the "What's Working" and "Needs Attention" summaries.
3. **Tracking** — ongoing notes about how supports play out day to day.
4. **My Insights** — chat with the local AI about your own data.
5. **Export Twin** — get your data out, in two very different ways:

| Export | Contains | Use it for |
|---|---|---|
| JSON / Excel / Word | **Everything**, including your name, history, and stakeholders | Your own backup, or trusted settings like an IEP meeting |
| **Share Overview (.md)** | A **de-identified summary** — no name, history, stakeholders, or AI chats | Giving a teacher a working picture of what helps you |

### Sharing an Overview with a Teacher

Click **Share Overview (.md)** on the Export page. A review screen opens
with a draft the app has already de-identified:

- Your strengths and goals appear as broad themes
  (e.g. "Creative expression" instead of specific personal details).
- Support descriptions and outcome notes are scrubbed: names, emails,
  phone numbers, and school names are automatically removed.
- Dates are reduced to seasons (e.g. "Summer 2026").
- Your name, history, stakeholders, and AI conversations are **never
  included at all**.

Then you are in control:

1. **Pick your alias** — the teacher sees "Student K4" (or whatever you
   choose), never your name.
2. **Read the draft.** The screen lists everything that was automatically
   removed. You can edit the text directly if anything still feels too
   personal. What you see is exactly what the teacher gets — nothing more.
3. **Run AI Privacy Check** (optional) — your local AI reads the draft
   and flags anything the automatic rules missed. This works only with
   local AI; your draft is never sent to a cloud service.
4. **Save & Share** — confirm, save the `.md` file, and give it only to
   teachers you feel safe with (thumb drive, email, however you like).

> **Honest limits:** automatic scrubbing is careful but not perfect —
> your own review is the real safeguard. And a teacher who knows you may
> still recognize you from context; sharing the file is always your
> choice of *who* to trust, not a guarantee of anonymity.

---

## For Teachers

You run your **own** AccessTwin with a Teacher account. Students appear
in your portal only when they (or their families) give you a file.

**Two ways to receive a student:**

- **Import Overview (.md)** — the de-identified file a student shared.
  The student appears under their alias (e.g. "Student K4") with their
  supports, ratings, and strength themes.
- **Import Twin (JSON)** — a complete twin, including identity. Only for
  full-trust situations (e.g. shared directly by the family).

**Working with a student's twin:**

- **Consult Coach** — the main tool for testing ideas. Ask things like
  *"I'm planning a video-heavy unit — what should I adapt for this
  student?"* The local AI answers grounded in the student's actual
  supports and effectiveness ratings, framed by UDL and POUR principles.
- **Copy AI Prompt** — prefer your own AI tool (e.g. one your district
  provides)? One click copies a ready-made coaching prompt containing
  the overview, UDL/POUR framing, and a privacy reminder. This button
  appears **only for overview imports** — full twins contain real names
  and should never be pasted into external AI tools.
- **Evaluate Document** — upload a lesson plan or material and link it
  to the student for evaluation.
- **Log Implementation / Tracking / Insights** — record what you tried,
  rate how it went, and watch effectiveness trends build over time.

**If you use an external AI tool:** never add the student's name, school,
or other identifying details to the conversation — and check your
district's policy on AI tools first. The overview file repeats this
reminder in its header.

---

## The Privacy Model in One Picture

```
STUDENT'S DEVICE                          TEACHER'S DEVICE
┌─────────────────────────┐               ┌─────────────────────────┐
│ Full twin (encrypted):  │               │ "Student K4":           │
│ name, history, people,  │   one .md     │ supports, ratings,      │
│ chats, everything       │   file, by    │ themes — no identity    │
│                         │ ─ student's ─▶│                         │
│ Student reviews & edits │   choice      │ Teacher's notes & coach │
│ before anything leaves  │               │ chats stay local too    │
└─────────────────────────┘               └─────────────────────────┘
```

The de-identification happens **before** the file leaves the student's
device, and the student approves the exact text. Even the teacher's own
accumulated notes can't reveal who the student is, because the identity
never entered their system.

Every export is recorded in the app's local audit log.

---

## The Loop

1. Student documents supports and rates what actually helps.
2. Student shares a de-identified overview with a teacher they trust.
3. Teacher tests ideas against it — in-app coach or their own AI — and
   logs what they try.
4. Student keeps full ownership of the real record the entire time.
