# Briscola in 5

![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

**Briscola in 5** is a digital implementation of the classic Italian card game "Briscola in 5" (also known as *Call-ace*), developed in Python. The project includes the **game engine**, a Command Line Interface (CLI), and playable bots.

---

## ⚙️ How it works

1. **Dealing:** The 40-card Sicilian deck is dealt equally among 5 players.
2. **The Auction:** Players compete by declaring a target score (from 61 to 120) and the trump suit (*Briscola*).
3. **The Partner:** The auction winner "calls" a card; whoever holds it becomes their secret partner.
4. **Gameplay:** 8 rounds where strategy and point counting are essential.
5. **Evaluation:** Final score calculation to determine if the pair (Caller+Partner) reached their goal.

---

## 🚀 Launching the game
To start a quick game directly in your terminal:
```bash
python -m briscola5.cli.main
```

---

## 🛠️ Project Architecture
```text
briscola5/
├── .github/workflows/    # CI Pipeline (GitHub Actions)
├── src/
│   ├── domain/           # Game logic, deck management and rules
│   ├── application/      # Match orchestration
│   ├── bots/             # Bot implementations 
│   └── cli/              # Command-line interface
├── tests/                # Unit tests
├── README.md
├── .gitignore
├── .flake8               # Configuration for linting
└── pyproject.toml        # Project configuration and dependencies
```

---

## 🔭 Next Steps
- [ ] **New GUI**: Implementation with Pygame, Tkinter or other libraries.
- [ ] **Advanced AI**: Bots based on probabilities and counting remaining cards.
- [ ] **Multiplayer**: Support for playing over a local network via Socket.

---

## 🤝 Contributing

We love contributions! Whether you are an expert in Briscola or a Python enthusiast, your help is welcome.

Before getting started, take a look at our **[Contribution Guidelines](./CONTRIBUTING.md)** for details on:
- How to set up the development environment.
- Standards for **Conventional Commits**.
- How to run tests and linting.

---

## ❤️ Support the project
If this simulator was useful for an exam or for fun, leave a ⭐ on GitHub!
