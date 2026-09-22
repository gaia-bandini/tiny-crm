"""Business rules of Tiny CRM: stages, search, follow-ups and the home-page numbers."""
from datetime import date

import db

# The pipeline, in order. A lead moves left to right and ends in won or lost.
STAGES = ["new", "contacted", "proposal", "won", "lost"]
SOURCES = ["referral", "website", "linkedin", "event"]


def today_text():
    """Return today's date as text in the same format we store, e.g. 2026-09-05."""
    return str(date.today())


# ---------- leads ----------

def all_leads():
    """Return every lead as a list of dicts, in the order of the CSV."""
    return db.load_table("leads")


def get_lead(lead_id):
    """Find one lead by id. Returns the lead dict, or None if it does not exist."""
    for lead in all_leads():
        if lead["id"] == str(lead_id):
            return lead
    return None


def leads_in_stage(stage):
    """Return the leads that are currently in the given stage."""
    matching = []
    for lead in all_leads():
        if lead["stage"] == stage:
            matching.append(lead)
    return matching


def count_by_stage(stage):
    """Count how many leads are currently in the given stage."""
    return len(leads_in_stage(stage))


def search_leads(query):
    """Return the leads whose name or company contains the search text."""
    results = []
    query = query.lower()
    for lead in all_leads():
        if query in lead["name"].lower() or query in lead["company"].lower():
            results.append(lead)
    return results


def add_lead(name, company, source, value, followup_on):
    """Create a lead in the 'new' stage, save it, and return its new id."""
    lead = {
        "id": db.next_id("leads"),
        "name": name,
        "company": company,
        "source": source,
        "stage": "new",
        "value": value,
        "followup_on": followup_on,
        "created_on": today_text(),
        "closed_on": "",
    }
    db.append_row("leads", lead)
    return lead["id"]


def save_lead(changed):
    """Write one changed lead back into leads.csv, keeping every other lead as it was."""
    leads = all_leads()
    for position in range(len(leads)):
        if leads[position]["id"] == changed["id"]:
            leads[position] = changed
    db.save_table("leads", leads)


def delete_lead(lead_id):
    """Remove one lead from leads.csv."""
    remaining = []
    for lead in all_leads():
        if lead["id"] != str(lead_id):
            remaining.append(lead)
    db.save_table("leads", remaining)


# ---------- stages ----------

def next_stage(stage):
    """Return the stage after this one, or None when the deal is already closed."""
    if stage == "new":
        return "contacted"
    if stage == "contacted":
        return "proposal"
    # proposal is the last step: from there you mark the deal won or lost
    return None


def move_to_next_stage(lead_id):
    """Push a lead one step along the pipeline and record it as an activity."""
    lead = get_lead(lead_id)
    following = next_stage(lead["stage"])
    if following is None:
        return
    lead["stage"] = following
    save_lead(lead)
    record_activity(lead_id, "moved to " + following)


def move_to_stage(lead_id, stage):
    """Move a lead to any stage, checking that the move is allowed."""
    # TODO: validate the transition and record the activity


def mark_won(lead_id):
    """Close a lead as won."""
    lead = get_lead(lead_id)
    lead["stage"] = "won"
    lead["closed_on"] = today_text()
    save_lead(lead)
    record_activity(lead_id, "won")


# ---------- notes and activities ----------

def notes_for(lead_id):
    """Return the notes of one lead, oldest first."""
    notes = []
    for note in db.load_table("notes"):
        if note["lead_id"] == str(lead_id):
            notes.append(note)
    return notes


def add_note(lead_id, text):
    """Attach a note to a lead and save it."""
    note = {
        "id": db.next_id("notes"),
        "lead_id": lead_id,
        "text": text,
        "created_on": today_text(),
    }
    db.append_row("notes", note)


def activities_for(lead_id):
    """Return the activities (calls, emails, meetings, moves) of one lead."""
    activities = []
    for activity in db.load_table("activities"):
        if activity["lead_id"] == str(lead_id):
            activities.append(activity)
    return activities


def record_activity(lead_id, kind):
    """Save one activity row for a lead, dated today."""
    activity = {
        "id": db.next_id("activities"),
        "lead_id": lead_id,
        "kind": kind,
        "created_on": today_text(),
    }
    db.append_row("activities", activity)


# ---------- follow-ups and reports ----------

def parse_date(text):
    """Turn a stored date like 2026-9-5 or 2026-09-05 into a real date, so dates compare as dates."""
    year, month, day = text.split("-")
    return date(int(year), int(month), int(day))


def followup_date(lead):
    """Return the follow-up date of a lead as a real date; used for sorting."""
    return parse_date(lead["followup_on"])


def days_overdue(followup_on, today):
    """Return how many whole days a stored follow-up date is before today."""
    return (today - parse_date(followup_on)).days


def overdue_followups(today=None):
    """Return the open leads whose follow-up date is before today, oldest first."""
    if today is None:
        today = date.today()
    overdue = []
    for lead in all_leads():
        # a won or lost deal is finished, nobody needs to chase it
        if lead["stage"] == "won" or lead["stage"] == "lost":
            continue
        if lead["followup_on"] == "":
            continue
        if parse_date(lead["followup_on"]) < today:
            overdue.append(lead)
    overdue.sort(key=followup_date)
    return overdue


def overdue_report(today=None):
    """Return the overdue open leads, oldest first, each with a days_overdue number added."""
    if today is None:
        today = date.today()
    report = []
    for lead in overdue_followups(today):
        item = dict(lead)
        item["days_overdue"] = days_overdue(lead["followup_on"], today)
        report.append(item)
    return report


def won_this_month(today=None):
    """Count the leads that were won during the current month."""
    if today is None:
        today = date.today()
    this_month = str(today)[:7]
    count = 0
    for lead in all_leads():
        if lead["stage"] != "won":
            continue
        if lead["closed_on"] == "":
            # a won lead without a close date means the data is incomplete
            continue
        if lead["closed_on"][:7] == this_month:
            count = count + 1
    return count
