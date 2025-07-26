PAWS – Personalized Automated Workflow System  
Hackathon Submission – WCHL25

Team  
- 2-member team  
- Backend: Email classification logic, storage system, and server coordination  
- Frontend: Desktop GUI built using Electron for seamless multi-PC operations  

Overview  
PAWS is an AI-powered email workflow assistant built for small-to-mid-sized B2B trading and logistics teams. It automates the repetitive process of handling business emails – fetching, classifying, storing, and distributing them across team PCs using a centralized server.  

With built-in support for decentralized storage and identity via Internet Computer Protocol (ICP), PAWS is future-ready for secure syncing, team collaboration, and remote access in distributed office setups. The server PC manages coordination, load balancing, and recovery to ensure no data is lost even during failures or unexpected interruptions.

What It Does  
- Connects to Gmail via IMAP  
- Classifies emails into categories: RFQs, Quotations, Invoices, Deliveries, Bank, and Spam  
- Detects and links reference numbers across email chains (e.g., RFQ ↔ Supplier Quote ↔ PO)  
- Stores emails as readable `.txt` files with attachments  
- Uses a central server to sync folders across multiple PCs  
- Logs all actions locally for traceability  
- ICP-ready: identity handling and decentralized backup integrated  

Tech Stack  
- Python – Core automation logic  
- Electron – GUI for client machines  
- SQLite – Local DB for mapping reference numbers  
- IMAP – Email access  
- Regex + ML – Email classification engine  
- ICP –  
  - Decentralized file storage  
  - Identity/authentication layer  
  - Future support for shared dashboards and remote syncing  

Built For  
- B2B trading companies and sourcing teams  
- Back offices handling structured email workflows  
- Logistics coordinators managing multi-step chains  
- Offices with 5–10 employees using shared computers  
- Teams seeking automation without costly SaaS tools  

Next Steps  
- Smarter ML classification with less manual rule-tuning  
- Enhanced UI for better user experience  
- Deeper ICP integration (shared dashboards, mobile syncing)
