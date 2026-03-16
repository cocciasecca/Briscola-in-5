# 🤝 Contributing to Briscola in 5

Thank you for your interest in contributing to **Briscola in 5**! Whether you are fixing a bug, adding a new bot strategy, or improving the documentation, your help is invaluable.

---

## 🛠️ Development Workflow

### 1. Fork and Clone
First, fork the repository on your GitHub profile and clone the fork locally:
```bash
git clone https://github.com/Dr-Faxzty/Briscola-in-5.git
cd Briscola-in-5
```

### 2. Environment Setup
Create a virtual environment and install the project with development dependencies:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# Install the project
pip install -e .
```

### 3. Create a Branch
Create a branch dedicated to your modification:
```bash
git checkout -b feature/new-feature
```

---

## 📝 Rules for Commits
We use the **Conventional Commits** standard to keep the history clean and readable. Messages must follow this format:

`<type>(<scope>): <description>`

**Common types**:
- `feat`: Addition of a new feature
- `fix`: Correction of a bug
- `docs`: Changes to documentation
- `style`: Modifications that do not affect the meaning of the code (whitespace, formatting, etc.)
- `refactor`: Code changes that do not add functionality or fix bugs
- `test`: Addition or correction of tests

**Example**: 
` feat(bot): added game strategy based on probabilities`

---

## 🧪 Test and Code Quality
Before submitting your changes, ensure everything works correctly.

1. Run the unit tests:
```bash
pytest tests/
```

2. Linting and formatting:
```bash
isort src/ tests/
black src/ tests/
flake8 src/ tests/
```

---

## 📢 Submitting a Pull Request

1. Run the **Push** of your branch on your fork:
```bash
git push origin feature/new-feature
```

2. Go to the original repository on GitHub.
3. Click on **"Compare & pull request"**.
4. Describe clearly the changes you have made and reference any open issues.

---

## 🙌 Thank you for your contribution!

If you have questions or need help, feel free to contact us by opening an Issue or participating in the discussion on GitHub. Every contribution, big or small, is highly appreciated!