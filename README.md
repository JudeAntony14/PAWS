PAWS - Personalized Automated Workflow System

Email Workflow Assistant for Businesses specifically B2B Trading companies.
Hackathon Submission – WCHL25

Abstract
 
PAWS (Personalized Automated Workflow System) is an AI-powered assistant built to automate and streamline business email handling at scale. Designed for small-to-mid-sized teams managing repetitive email tasks—like sourcing, logistics, and customer coordination—it fetches emails from Gmail, classifies them using AI logic, and organizes all content locally for team-wide access.

Whether it's recognizing RFQs, invoices, or linking a supplier quote to a client RFQ, PAWS does it automatically—saving hours of manual work each day. It's ideal for teams working across multiple shared PCs and dealing with high email volumes.

ICP integration is already live for decentralized storage and secure identity—laying the groundwork for even smarter and more collaborative workflows in the near future.

What It Does:

Connects to Gmail via IMAP

Uses AI/ML rules to classify emails into:

RFQs, Quotations, Invoices, Deliveries, Bank emails and Spam.

Detects and links reference numbers across email chains

Saves emails as readable .txt files with attachments in proper folders

Syncs across multiple PCs in the office setup

Logs everything locally for transparency

Connects to Gmail via IMAP

Classifies using regex and ML-based logic

Uses SQLite to map reference numbers (e.g. RFQ ↔ Quote ↔ PO)

Ready for ICP-based storage/identity systems

Tech Stack

Python – Core logic and automation

Electron – Desktop interface for client PCs

SQLite – Local reference database

IMAP – Gmail access and parsing

Regex + ML heuristics – Classification engine

ICP (Internet Computer Protocol) –

Decentralized storage

Identity management (already integrated)

Secure syncing between nodes

 Built For

Sourcing & trading companies

Logistics teams handling multi-step email trails

Back offices processing repetitive document-heavy tasks

Small-to-medium businesses with 5–10 employees using shared PCs

Teams that want smart automation without expensive SaaS tools

 Notes
Local-first, offline-ready

Works best with Gmail

Future updates:

Enhanced UI

Smarter ML models

Expanded ICP integrations (e.g., shared dashboard, decentralized access)

 Summary
PAWS transforms messy email workflows dealt by human employees into an organized, AI-driven system that can be tweaked to individual company requirements for real-world teams. 
