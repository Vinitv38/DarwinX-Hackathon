# Mission: 1 - Empathetic Code Reviewer 

> AI-powered tool that transforms critical code reviews into constructive, educational feedback

## 🚀 Features
- **AI-Powered**: Uses Groq's LLaMA-3 (70B) model
- **Educational**: Provides explanations and helpful resources
- **Simple CLI**: Easy to integrate into any workflow
- **Markdown Output**: Clean, well-formatted reports

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- [Groq API Key](https://console.groq.com/)

### Installation
```bash
# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key
echo "GROQ_API_KEY=your_api_key_here" > .env
```

## 🛠 Usage (Stand Out Feature)

### Basic Example
```bash
# Run with default example
python empathetic_reviewer.py
```

### Custom Input File
```bash
python empathetic_reviewer.py -i test_input.json -o review.md
```

### Input Format (`test_input.json`)
```json
{
    "code_snippet": "def example():\n    return 42",
    "review_comments": [
        "Add docstring",
        "Make more flexible"
    ]
}
```

## 📝 Example Output

```markdown
# Empathetic Code Review Report

## Analysis of Comment: "This is inefficient. Don't loop twice."

**Positive Rephrasing:** Let's optimize this function for better performance!

**The 'Why':** Using a single loop improves efficiency by reducing iterations.

**Suggested Improvement:**
```python
def get_active_users(users):
    return [user for user in users if user.is_active and user.profile_complete]
```

**Helpful Resources:**
- [List Comprehensions in Python](https://docs.python.org/3/tutorial/datastructures.html)
- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
```

## 🔧 Configuration

Edit these values in `empathetic_reviewer.py`:
```python
self.model = "llama3-70b-8192"  # Groq model
temperature = 0.3               # Response creativity
max_tokens = 1000              # Max response length
```

