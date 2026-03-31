from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Create a PDF document
pdf_file = "resume.pdf"
document = SimpleDocTemplate(pdf_file, pagesize=letter)

# Create a list to hold the content
content = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(name='Title', fontSize=18, spaceAfter=12)
heading_style = ParagraphStyle(name='Heading', fontSize=14, spaceAfter=6, textColor=colors.black)
normal_style = styles['Normal']

# Add content to the PDF
content.append(Paragraph("ABHISHEK B GOURI", title_style))
content.append(Paragraph("📧 Email: abhinbg025@gmail.com | 📱 Phone: 8660349352", normal_style))
content.append(Paragraph("🔗 LinkedIn: www.linkedin.com/in/abhishek-b-gouri", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("CAREER OBJECTIVE", heading_style))
content.append(Paragraph("Aspiring Backend Developer with strong skills in Django, REST APIs, and backend systems. Eager to apply problem-solving abilities and technical expertise to real-world projects. Passionate about building scalable applications and continuous learning.", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("EDUCATION", heading_style))
content.append(Paragraph("B.E. in Computer Science and Engineering – Visvesvaraya Technological University (VTU) – 2026 (Pursuing)", normal_style))
content.append(Paragraph("PUC (Karnataka Board) – 72%", normal_style))
content.append(Paragraph("SSLC (KSEEB) – 94%", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("PROJECTS", heading_style))
content.append(Paragraph("College Projects", normal_style))
content.append(Paragraph("Mini Project: Age & Sentiment Analysis using ML", normal_style))
content.append(Paragraph("Built a machine learning model to predict age and analyze sentiment from text.", normal_style))
content.append(Paragraph("Implemented preprocessing pipelines and applied ML classification algorithms.", normal_style))
content.append(Paragraph("Delivered insights with accuracy using Python and Scikit-learn.", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("Major Project: AI-Powered Auto-Healing Cloud Infrastructure", normal_style))
content.append(Paragraph("Designed a system that detects failures in cloud environments and triggers auto-healing.", normal_style))
content.append(Paragraph("Integrated AI models for anomaly detection in server health metrics.", normal_style))
content.append(Paragraph("Improved system uptime and resilience by automating recovery processes.", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("Other Projects", normal_style))
content.append(Paragraph("MedCloud – Privacy-Focused Medical Cloud Storage", normal_style))
content.append(Paragraph("Developed a Django-based cloud storage platform for sensitive medical records.", normal_style))
content.append(Paragraph("Implemented encryption/decryption with AWS S3 integration.", normal_style))
content.append(Paragraph("Ensured secure file sharing between patients and doctors.", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("Remote Work Task & Role Manager (with Chat & RBAC)", normal_style))
content.append(Paragraph("Built a task management system with role-based access and team collaboration features.", normal_style))
content.append(Paragraph("Implemented JWT authentication and REST APIs in Django.", normal_style))
content.append(Paragraph("Added Slack-style real-time chat and notifications.", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("TECHNICAL SKILLS", heading_style))
content.append(Paragraph("Programming Languages: Python, Java, SQL", normal_style))
content.append(Paragraph("Frameworks & Tools: Django, REST API, HTML/CSS, Git, AWS (S3, KMS)", normal_style))
content.append(Paragraph("Databases: MySQL, PostgreSQL, SQLite", normal_style))
content.append(Paragraph("Concepts: Authentication (JWT, Session), RBAC, Cloud Security, Encryption, Data Structures & Algorithms", normal_style))
content.append(Spacer(1, 12))

content.append(Paragraph("SOFT SKILLS", heading_style))
content.append(Paragraph("Strong Problem-Solving & Debugging", normal_style))
content.append(Paragraph("Team Collaboration & Communication", normal_style))
content.append(Paragraph("Time Management & Adaptability", normal_style))
content.append(Paragraph("Quick Learner & Self-Motivated", normal_style))

# Build the PDF
document.build(content)

print(f"PDF generated successfully: {pdf_file}")
