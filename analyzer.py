import argparse
import csv
import re
from pathlib import Path


PROMOTIONAL_PHRASES = (
    "buy now", "limited time", "special offer", "promo code", "click here",
    "subscribe now", "claim your prize", "business opportunity", "make money fast",
)
BUG_TERMS = (
    "crash", "crashes", "crashed", "error", "bug", "broken", "not working",
    "fails", "failed", "failure", "freezes", "frozen", "can't log in", "cannot log in",
    "slow", "problem", "issue",
)
BILLING_TERMS = (
    "billing", "bill", "payment", "charged", "charge", "invoice", "refund",
    "subscription", "payment method",
)
FEATURE_TERMS = (
    "feature request", "would be awesome if", "would love", "could you add",
    "please add", "add a", "add an", "suggest", "request a", "request an",
    "it would be great", "wish you had", "support for",
)
URGENT_TERMS = ("asap", "urgent", "immediately", "critical", "right away")
HIGH_TERMS = ("can't use", "cannot use", "unable to", "blocking", "charged twice")
POSITIVE_TERMS = ("awesome", "great", "love", "excellent", "thank you", "thanks", "happy", "helpful")
NEGATIVE_TERMS = (
    "crash", "crashes", "crashed", "error", "bug", "broken", "not working", "fails",
    "failed", "failure", "freezes", "problem", "frustrated", "disappointed", "unhappy",
    "charged twice", "can't", "cannot", "never",
)
PRODUCT_FEATURES = (
    "payment page", "dark mode", "checkout", "mobile app", "website", "dashboard",
    "login", "search", "notifications", "account", "subscription", "Chrome",
)
GREETINGS = re.compile(r"\b(hi|hello|hey|dear|good morning|good afternoon|good evening)\b", re.I)
PLEASANTRIES = re.compile(r"\b(hope you are having a nice day|hope you’re having a nice day|hope you are well|how are you)\b", re.I)


def contains_any(text, terms):
    return any(term in text for term in terms)


def rejection_reason(message):
    text = message.strip().lower()
    if not text:
        return "Empty message"
    if contains_any(text, PROMOTIONAL_PHRASES):
        return "Promotional or spam message"

    remaining = PLEASANTRIES.sub("", text)
    remaining = GREETINGS.sub("", remaining).strip(" ,.!?\t\n")
    actionable = (
        contains_any(text, BUG_TERMS + BILLING_TERMS + FEATURE_TERMS)
        or contains_any(text, POSITIVE_TERMS + NEGATIVE_TERMS)
        or "?" in text
        or bool(re.search(r"\b(can|could|would|what|when|where|why|how|please|want|need|wish)\b", text))
    )
    if not remaining or not actionable:
        return "Greeting or non-actionable message"
    return ""


def classify(message):
    text = message.lower()
    if contains_any(text, BUG_TERMS):
        category = "Bug Report"
    elif contains_any(text, FEATURE_TERMS):
        category = "Feature Request"
    elif contains_any(text, BILLING_TERMS):
        category = "Billing Issue"
    else:
        category = "General Inquiry"

    if contains_any(text, URGENT_TERMS):
        priority = "Urgent"
    elif contains_any(text, HIGH_TERMS):
        priority = "High"
    elif category == "Bug Report":
        priority = "High"
    elif category == "Feature Request":
        priority = "Medium"
    elif category == "Billing Issue":
        priority = "Medium"
    else:
        priority = "Low"

    positive = sum(text.count(term) for term in POSITIVE_TERMS)
    negative = sum(text.count(term) for term in NEGATIVE_TERMS)
    sentiment = "Positive" if positive > negative else "Negative" if negative > positive else "Neutral"

    mentions = [(text.find(term.lower()), term) for term in PRODUCT_FEATURES if term.lower() in text]
    product_feature = min(mentions)[1].title() if mentions else "Not specified"
    return category, priority, sentiment, product_feature


def suggest_reply(category, product_feature):
    item = product_feature if product_feature != "Not specified" else "your concern"
    replies = {
        "Bug Report": f"Thank you for reporting the issue with {item}. We’re sorry for the disruption; our team will review it.",
        "Feature Request": f"Thank you for suggesting {item}. We appreciate your feedback and will share it with our product team.",
        "Billing Issue": "Thank you for contacting us about your billing concern. We’ll review it and follow up with you.",
        "General Inquiry": "Thank you for reaching out. We appreciate your message and will get back to you soon.",
    }
    return replies[category]


def analyze(ticket):
    message = ticket["message"].strip()
    reason = rejection_reason(message)
    result = {
        "ticket_id": ticket["ticket_id"],
        "message": message,
        "status": "Ignored" if reason else "Processed",
        "category": "",
        "priority": "",
        "sentiment": "",
        "product_feature": "",
        "suggested_auto_reply": "",
    }
    if not reason:
        category, priority, sentiment, product_feature = classify(message)
        result.update({
            "category": category,
            "priority": priority,
            "sentiment": sentiment,
            "product_feature": product_feature,
            "suggested_auto_reply": suggest_reply(category, product_feature),
        })
    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze customer feedback from a CSV file.")
    parser.add_argument("input", nargs="?", default="sample_tickets.csv", help="Input CSV with ticket_id and message columns")
    parser.add_argument("output", nargs="?", default="analysis_results.csv", help="Output CSV path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    with input_path.open(newline="", encoding="utf-8-sig") as source:
        tickets = csv.DictReader(source)
        if not tickets.fieldnames or not {"ticket_id", "message"}.issubset(tickets.fieldnames):
            parser.error("Input CSV must contain ticket_id and message columns")
        results = [analyze(ticket) for ticket in tickets]

    fields = ("ticket_id", "message", "status", "category", "priority", "sentiment", "product_feature", "suggested_auto_reply")
    with output_path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    print(f"Analyzed {len(results)} messages; results saved to {output_path}.")


if __name__ == "__main__":
    main()
