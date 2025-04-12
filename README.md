# LLM-BASED-ESSAY-SCORING-SYSTEM
A full-stack web application that allows admins to generate essay rubrics using LLMs, and users to write and submit essays for automated scoring and feedback. Built with Flask, MySQL, and custom evaluation + feedback logic powered by LLMs. Supports rubric editing, essay history tracking, and feedback storage.
## ✨ Features

### 👨‍🏫 Admin Panel
- Generate essay structure using LLM (based on topic and difficulty)
- View and edit auto-generated structure
- Finalize and save rubrics to the database
- View all previously created rubrics in a readable format

### 👩‍🎓 User Panel
- View essay topics with structure
- Write essays based on selected rubric
- Submit essays for LLM-based scoring
- Receive scores (grammar, content, structure, conclusion)
- Get personalized feedback
- View submission history with stored feedback

---

## ⚙️ Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Backend      | Python, Flask                        |
| Frontend     | HTML, CSS (Dark Mode), JavaScript    |
| Database     | MySQL                                |
| LLM API      | Custom-configured LLM (e.g., OpenAI, local) |
| AI Modules   | Essay structure generator, evaluator, feedback system |

---

## 🛠️ Setup Instructions

1. **Clone the Repository**
git clone https://github.com/your-username/LLM-BASED-ESSAY-SCORING-SYSTEM.git
2. **Install Required Packages**
pip install -r requirements.txt
3. **Set Up MySQL Database**
Create a database and use sql file in repo
Update config.ini with your MySQL credentials and secret key.
4. **python app.py**

5. **repo structure**
├── app.py
├── config.ini
├── structure_service.py
├── evaluation_service.py
├── feedback_service.py
├── requirements.txt
├── schema.sql
├── templates/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── admin_previous_work.html
│   └── user/
│       ├── dashboard.html
│       └── submitessay.html
├── static/
│   ├── styles.css
│   ├── admin.css
│   ├── admin_previous.css
│   └── script.js


![Structure_Eng](https://github.com/user-attachments/assets/60b0a0e0-6f46-41db-9cad-a39edd7cf460)


![Previous_Work_Admin](https://github.com/user-attachments/assets/bae9cc6b-b491-414f-ae68-67b1e892c8c7)


![Previous_essay_user](https://github.com/user-attachments/assets/5a639487-74c1-4d94-8ac0-801cf324f56e)

