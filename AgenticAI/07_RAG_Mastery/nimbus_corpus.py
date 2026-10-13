"""Small fake knowledge base for the RAG labs (35, 36, 37).

Each document is already "chunk sized" so the labs can focus on search, not splitting.
It contains deliberate traps that real RAG systems hit:
  - synonyms      : users say "vacation", docs say "annual leave"
  - exact codes   : error codes E-4021 vs E-4012, SKU numbers
  - old versions  : the 2024 leave policy (v3) conflicts with the 2026 one (v4)
  - multi-hop     : NimbusDB -> owned by Storage team -> Storage on-call policy
  - look-alikes   : "cancel subscription" vs "start subscription"
"""

DOCS = [
    {"id": "hr-leave-v4", "title": "Annual Leave Policy (v4, 2026)", "department": "HR", "updated_at": "2026-03-01",
     "text": "Full-time employees get 24 days of paid annual leave per calendar year. Leave accrues at 2 days per month. "
             "Up to 8 unused days can be carried over to the next year; days above 8 expire on 31 March."},
    {"id": "hr-leave-v3", "title": "Annual Leave Policy (v3, 2024, superseded)", "department": "HR", "updated_at": "2024-01-10",
     "text": "Full-time employees get 20 days of paid annual leave per year. Unused leave cannot be carried over. "
             "This version is superseded by v4."},
    {"id": "hr-intern-leave", "title": "Intern Leave Rules", "department": "HR", "updated_at": "2026-02-01",
     "text": "Interns earn 1.5 days of paid leave for every month of their internship. Intern leave cannot be carried over "
             "and is not paid out when the internship ends."},
    {"id": "hr-sick", "title": "Sick Leave", "department": "HR", "updated_at": "2026-01-15",
     "text": "Sick leave is separate from annual leave: 10 days per year. A doctor's note is required for absences longer than 2 consecutive days."},
    {"id": "hr-parental", "title": "Parental Leave", "department": "HR", "updated_at": "2026-01-15",
     "text": "Birthing parents get 26 weeks of paid parental leave; non-birthing parents get 6 weeks. It can be taken within 12 months of the birth or adoption."},
    {"id": "hr-holidays", "title": "Public Holiday Calendar", "department": "HR", "updated_at": "2026-01-01",
     "text": "The company observes 12 public holidays per year. The India office follows the national calendar plus Diwali and Holi; "
             "the US office follows federal holidays plus Thanksgiving Friday."},
    {"id": "hr-review", "title": "Performance Reviews", "department": "HR", "updated_at": "2026-01-01",
     "text": "Performance reviews happen twice a year, in June and December. Employees write a self-review, then the manager "
             "rates impact on a 5-point scale."},
    {"id": "fin-internet", "title": "Remote Work Internet Allowance", "department": "Finance", "updated_at": "2026-01-20",
     "text": "Employees who work remotely can claim up to 1500 INR per month for home broadband. Submit the bill in the "
             "expense tool before the 5th of the next month."},
    {"id": "fin-travel", "title": "Travel Expense Policy", "department": "Finance", "updated_at": "2025-11-01",
     "text": "Book flights in economy class for trips under 6 hours. Hotel limit is 8000 INR per night in metro cities. "
             "Keep all receipts; claims without receipts are rejected."},
    {"id": "fin-meals", "title": "Meal Reimbursement", "department": "Finance", "updated_at": "2025-11-01",
     "text": "During business travel, meals are reimbursed up to 1200 INR per day. Alcohol is never reimbursed."},
    {"id": "it-vpn-reset", "title": "Reset your VPN password", "department": "IT", "updated_at": "2026-02-10",
     "text": "To reset your VPN password, open the self-service portal, choose 'Forgot VPN password', and confirm with your "
             "authenticator app. The new password works after 5 minutes."},
    {"id": "it-vpn-mac", "title": "VPN setup on macOS", "department": "IT", "updated_at": "2026-02-10",
     "text": "Install the GlobalConnect VPN client from the Self Service app, sign in with your company email, and allow the "
             "system extension in macOS Privacy & Security settings."},
    {"id": "it-password", "title": "Password Policy", "department": "IT", "updated_at": "2025-09-01",
     "text": "Account passwords must be at least 14 characters. Multi-factor authentication is mandatory. Passwords are "
             "no longer rotated every 90 days unless a breach is suspected."},
    {"id": "it-laptop", "title": "Laptop Policy", "department": "IT", "updated_at": "2025-08-01",
     "text": "New joiners receive a MacBook Pro. Laptops are refreshed every 3 years. A lost laptop must be reported to IT "
             "within 24 hours so it can be wiped remotely."},
    {"id": "sec-incident", "title": "Reporting a Security Incident", "department": "Security", "updated_at": "2026-01-05",
     "text": "If you suspect phishing, malware, or a data leak, report it immediately in the #security-incidents channel "
             "or call the 24/7 security hotline. Do not try to investigate yourself."},
    {"id": "prod-e4021", "title": "Error E-4021: payment declined at checkout", "department": "Product", "updated_at": "2026-03-12",
     "text": "Error E-4021 means the card issuer declined the payment at checkout. Ask the customer to use another card or "
             "contact their bank. Do not retry more than 3 times."},
    {"id": "prod-e4012", "title": "Error E-4012: session expired", "department": "Product", "updated_at": "2026-03-12",
     "text": "Error E-4012 appears when the login session expired. The user should sign in again; their cart is saved for 24 hours."},
    {"id": "prod-e4120", "title": "Error E-4120: address verification failed", "department": "Product", "updated_at": "2026-03-12",
     "text": "Error E-4120 means the billing address does not match the card. Ask the customer to re-enter the postcode "
             "exactly as printed on their bank statement."},
    {"id": "prod-e4210", "title": "Error E-4210: payment gateway timeout", "department": "Product", "updated_at": "2026-03-12",
     "text": "Error E-4210 means our payment gateway did not respond in time. The card was not charged. Wait one minute "
             "and retry; if it repeats, check the status page."},
    {"id": "prod-e4201", "title": "Error E-4201: coupon code expired", "department": "Product", "updated_at": "2026-03-12",
     "text": "Error E-4201 is shown when a coupon code has expired or was already used. Expired coupons cannot be "
             "re-activated by support."},
    {"id": "prod-nimbusdb-tiers", "title": "NimbusDB pricing tiers", "department": "Product", "updated_at": "2026-02-20",
     "text": "NimbusDB is our managed vector database. The free tier includes 1 million vectors and 2 GB storage. The Pro "
             "plan costs 99 USD per month and adds backups and SSO."},
    {"id": "prod-nimbusdb-owner", "title": "NimbusDB ownership", "department": "Product", "updated_at": "2026-01-30",
     "text": "NimbusDB is built and operated by the Storage team. Product questions go to the Storage team's product manager."},
    {"id": "eng-storage-oncall", "title": "Storage team on-call", "department": "Engineering", "updated_at": "2026-02-02",
     "text": "The Storage team runs a 1-week on-call rotation with a primary and a secondary engineer. Pages must be "
             "acknowledged within 15 minutes; on-call engineers get one comp day per week on call."},
    {"id": "prod-cancel", "title": "Cancel a subscription", "department": "Product", "updated_at": "2026-01-12",
     "text": "Customers can cancel their subscription from Billing > Plan > Cancel. Access continues until the end of the "
             "paid period; no partial refunds are given."},
    {"id": "prod-start", "title": "Start a subscription", "department": "Product", "updated_at": "2026-01-12",
     "text": "Customers can start a subscription from Billing > Plan > Upgrade. The first 14 days are a free trial and the "
             "card is charged after the trial ends."},
    {"id": "prod-sku", "title": "Hardware SKU 88-1032", "department": "Product", "updated_at": "2025-12-01",
     "text": "SKU 88-1032 is the Nimbus Edge appliance with 64 GB RAM. It ships within 10 business days and has a 2-year warranty."},
    {"id": "hr-conduct", "title": "Code of Conduct", "department": "HR", "updated_at": "2025-06-01",
     "text": "Treat colleagues with respect. Harassment and discrimination are not tolerated. Report concerns to HR or the anonymous ethics line."},
]

# Labelled evaluation set: question -> ids of the chunk(s) that answer it.
# "kind" tells you which trap the question is testing.
EVAL = [
    {"q": "How many vacation days do I get per year?", "relevant": ["hr-leave-v4"], "kind": "synonym"},
    {"q": "Can I roll over unused holidays to next year?", "relevant": ["hr-leave-v4"], "kind": "synonym"},
    {"q": "How much time off do interns get?", "relevant": ["hr-intern-leave"], "kind": "synonym"},
    {"q": "What does E-4021 mean?", "relevant": ["prod-e4021"], "kind": "exact code"},
    {"q": "customer sees E-4012", "relevant": ["prod-e4012"], "kind": "exact code"},
    {"q": "SKU 88-1032 warranty", "relevant": ["prod-sku"], "kind": "exact code"},
    {"q": "E-4210", "relevant": ["prod-e4210"], "kind": "exact code"},
    {"q": "user got E-4120 when paying", "relevant": ["prod-e4120"], "kind": "exact code"},
    {"q": "what to tell a customer about E-4201", "relevant": ["prod-e4201"], "kind": "exact code"},
    {"q": "Does unused leave expire, and when?", "relevant": ["hr-leave-v4"], "kind": "old version"},
    {"q": "What is the on-call rotation length for the team that runs NimbusDB?", "relevant": ["eng-storage-oncall"], "kind": "multi-hop"},
    {"q": "I forgot my VPN password", "relevant": ["it-vpn-reset"], "kind": "keyword"},
    {"q": "Can I get my home wifi bill refunded?", "relevant": ["fin-internet"], "kind": "synonym"},
    {"q": "How do I stop paying for my plan?", "relevant": ["prod-cancel"], "kind": "look-alike"},
    {"q": "How many vectors are free in NimbusDB?", "relevant": ["prod-nimbusdb-tiers"], "kind": "keyword"},
    {"q": "Who maintains NimbusDB?", "relevant": ["prod-nimbusdb-owner"], "kind": "synonym"},
    {"q": "What should I do if I clicked a suspicious email link?", "relevant": ["sec-incident"], "kind": "synonym"},
    {"q": "Do I need to change my password every 3 months?", "relevant": ["it-password"], "kind": "synonym"},
    {"q": "How long is maternity leave?", "relevant": ["hr-parental"], "kind": "synonym"},
    {"q": "Is beer covered when travelling for work?", "relevant": ["fin-meals"], "kind": "synonym"},
    {"q": "I lost my MacBook, what now?", "relevant": ["it-laptop"], "kind": "keyword"},
]
