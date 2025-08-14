# Empathetic Code Reviewer

Transform critical code review comments into constructive, educational feedback using AI.

## 🚀 Features

- AI-powered code review feedback using Groq's LLM
- Context-aware responses based on comment severity
- Educational explanations with relevant resources
- Multiple output formats (console/file)
- Configurable behavior through JSON config
- Simple command-line interface

## 🛠️ Technical Approach

This project uses Groq's API to access open-source AI models for generating empathetic code reviews. The system is designed to:

1. **Input Processing**: Accepts code snippets and review comments
2. **Context Analysis**: Determines severity and appropriate tone
3. **AI-Powered Review**: Uses Groq's LLM for generating constructive feedback
4. **Output Generation**: Formats responses in Markdown with clear sections

### Why Groq?
- Access to powerful open-source models
- Fast inference speeds
- Simple API integration
- Generous free tier for testing

## Quick Start

### Basic Usage
```bash
# Run with default example (prints to console)
python empathetic_reviewer.py

# Save output to a file
python empathetic_reviewer.py -o review.md

# Use a custom input file
python empathetic_reviewer.py -i my_code.json -o review.md
```

### Input Format
Create a JSON file (e.g., `my_code.json`):
```json
{
    "code_snippet": "def example():\n    # Your code here\n    pass",
    "review_comments": [
        "This function is too simple",
        "Add proper error handling"
    ]
}
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd empathetic-code-reviewer
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get Groq API Key**
   - Sign up at [Groq Cloud](https://console.groq.com/)
   - Create an API key in the dashboard
   - Create a `.env` file:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

## 🧪 Testing the Application

### Basic Test
```bash
# Run with default example
python empathetic_reviewer.py
```

### Test with Custom Input
1. Create a test file `test_input.json`:
   ```json
   {
       "code_snippet": "def add(a, b):\n    return a + b",
       "review_comments": [
           "This function is too simple",
           "Add input validation"
       ]
   }
   ```

2. Run the test:
   ```bash
   python empathetic_reviewer.py -i test_input.json -o test_output.md
   ```

### Expected Output
- Console output showing the review process
- Generated `test_output.md` with the review

### Verifying the Output
Check that the output includes:
- Constructive feedback for each comment
- Code improvements (if applicable)
- Educational explanations
- Proper Markdown formatting

## Features

- Converts critical code review comments into supportive, educational feedback
- Provides clear explanations of coding principles
- Suggests improved code implementations
- Generates a well-formatted Markdown report

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Groq API key](https://console.groq.com/)

### Installation

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/empathetic-code-reviewer.git
   cd empathetic-code-reviewer
   ```

2. **Setup environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Setup your API key
   cp .env.example .env
   # Edit .env and add your Groq API key

## Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd empathetic-code-reviewer
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

## 🚀 Three Ways to Use the Empathetic Code Reviewer

### 1. Basic Usage (Console Output Only)
Run with default example to see the output in your console:
```bash
python empathetic_reviewer.py
```

### 2. Save Report to a File
Generate and save the review report to a Markdown file:
```bash
python empathetic_reviewer.py -o review_report.md
```

### 3. Use Custom Input File
Provide your own JSON file with code and review comments:
```bash
python empathetic_reviewer.py -i my_review.json -o review_report.md
```

## 📝 Input File Format

Create a JSON file (e.g., `my_review.json`) with this structure:
```json
{
    "code_snippet": "def example_function():\n    pass",
    "review_comments": [
        "This function doesn't do anything.",
        "Add proper error handling.",
        "Consider adding type hints."
    ]
}
```

## 🔍 Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-o, --output` | Save report to a file | `-o review.md` |
| `-i, --input` | Use a custom JSON input file | `-i my_review.json` |
| (none) | Use default example and print to console | `python empathetic_reviewer.py` |

## Example Output

```markdown
# Empathetic Code Review Report

## Analysis of Comment 1: "This is inefficient. Don't loop twice conceptually."

* **Positive Rephrasing:** "Great job on the logic! Let's make this more efficient by combining the loops."
* **The 'Why':** Using a single loop improves performance by reducing the number of iterations over the data.
* **Suggested Improvement:**
```python
def get_active_users(users):
    return [user for user in users if user.is_active and user.profile_complete]
```

---

## Summary

Here's a summary of the suggested improvements. Each recommendation is designed to help improve code quality while being constructive and supportive. Remember, every piece of code is an opportunity to learn and grow as a developer!
```

## Configuration

You can modify the following in the script:
- `model`: Change the Groq model (default: "llama3-70b-8192")
- `temperature`: Adjust the creativity of responses (default: 0.3)
- `max_tokens`: Control the maximum length of the response (default: 1000)

## Configuration

Customize the reviewer's behavior by creating a `config.json` file:

```json
{
    "tone": "friendly",
    "language_level": "intermediate",
    "include_resources": true,
    "max_suggestions": 3
}
```
