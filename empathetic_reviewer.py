import json
import os
import re
import sys
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, validator
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default configuration
DEFAULT_CONFIG = {
    "model": "llama3-70b-8192",
    "temperature": 0.3,
    "max_tokens": 1000,
    "tone": "friendly",
    "language_level": "intermediate",
    "include_resources": True,
    "max_suggestions": 3,
    "severity_thresholds": {
        "high": ["error", "critical", "fatal", "never", "always"],
        "medium": ["warning", "issue", "problem", "concern"],
        "low": ["suggestion", "consider", "maybe", "perhaps"]
    },
    "output": {
        "include_original_comment": True,
        "include_severity": True,
        "include_timestamp": True
    }
}

class Config(BaseModel):
    model: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: int = Field(gt=0)
    tone: Literal["friendly", "professional", "encouraging"]
    language_level: Literal["beginner", "intermediate", "advanced"]
    include_resources: bool
    max_suggestions: int = Field(gt=0)
    severity_thresholds: Dict[str, List[str]]
    output: Dict[str, bool]

    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Temperature must be between 0 and 1')
        return v

def load_config(config_path: str = None) -> Config:
    """Load configuration from file or use defaults."""
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_data = {**DEFAULT_CONFIG, **json.load(f)}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in config file. Using defaults.", file=sys.stderr)
            config_data = DEFAULT_CONFIG
    else:
        config_data = DEFAULT_CONFIG
    
    return Config(**config_data)

class ReviewComment(BaseModel):
    original: str
    positive_rephrasing: str
    explanation: str
    suggested_code: str = ""
    resources: List[Dict[str, str]] = []

class CodeReviewRequest(BaseModel):
    code_snippet: str
    review_comments: List[str]

class EmpatheticReviewer:
    def __init__(self, config: Config = None):
        """Initialize the reviewer with configuration."""
        self.config = config or load_config()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
    def _extract_json_from_text(self, text: str) -> Optional[dict]:
        """Extract JSON from text using regex."""
        try:
            # Look for JSON-like content between triple backticks
            match = re.search(r'```(?:json)?\n({.*?})\n```', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
                
            # If no code block, try to find JSON in the text
            match = re.search(r'({.*})', text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
                
            return None
        except (json.JSONDecodeError, AttributeError):
            return None
    
    def _get_severity_level(self, comment: str) -> str:
        """Determine the severity level of a comment based on config."""
        comment_lower = comment.lower()
        for level, words in self.config.severity_thresholds.items():
            if any(word in comment_lower for word in words):
                return level
        return "medium"  # Default to medium severity
    
    def _get_tone_guidance(self, severity: str) -> str:
        """Get tone guidance based on severity."""
        return {
            'high': (
                "The original feedback was quite critical. Be extra empathetic and supportive. "
                "Acknowledge the effort while gently guiding towards improvement. Focus on being "
                "encouraging and constructive, not discouraging."
            ),
            'medium': (
                "The feedback is neutral or questioning. Provide clear, educational explanations. "
                "Be helpful and informative while maintaining a positive tone. Focus on knowledge sharing."
            ),
            'low': (
                "The feedback is minor or positive. Acknowledge what's working well and provide "
                "gentle suggestions for small improvements. Keep the tone light and encouraging."
            )
        }.get(severity, 'Provide constructive feedback with a positive and helpful tone.')
    
    def generate_review(self, code_snippet: str, comment: str) -> ReviewComment:
        """Generate an empathetic code review using Groq's API."""
        severity = self._get_severity_level(comment)
        tone_guidance = self._get_tone_guidance(severity)
        
        # Build system prompt based on configuration
        system_prompt = f"""You are an experienced senior developer providing a code review. 
        Your goal is to transform critical comments into constructive, educational feedback.
        
        Tone: {self.config.tone.capitalize()}
        Target Experience Level: {self.config.language_level.capitalize()}
        {tone_guidance}
        
        Key principles to follow:
        1. Always start with something positive or acknowledge the effort
        2. Explain the 'why' behind suggestions
        3. Provide clear, actionable improvements (max {self.config.max_suggestions} suggestions)
        {"4. Include relevant resources for learning" if self.config.include_resources else ""}
        5. End on an encouraging note
        
        Adjust your tone based on the severity of the original feedback.
        """.strip()
        
        user_prompt = f"""Code to review:
```python
{code_snippet}
```

Original review comment: "{comment}"

Please provide:
1. A positive rephrasing of the feedback
2. A clear explanation of the underlying principle
3. A suggested code improvement (if applicable) - IMPORTANT: Always include the complete function definition in suggested_code
4. Relevant resources (PEP links, style guides, etc.)

Format your response as a JSON object with these keys:
- positive_rephrasing (string)
- explanation (string)
- suggested_code (string, optional) - MUST include the complete function definition
- resources (array of objects with 'title' and 'url')

Example response for a function improvement:
```json
{{
  "positive_rephrasing": "Great job on the logic! Here's a suggestion to make it even better...",
  "explanation": "Using list comprehensions is more Pythonic and efficient because...",
  "suggested_code": "def get_active_users(users):\n    return [user for user in users if user.is_active and user.profile_complete]",
  "resources": [
    {{"title": "PEP 8 - Style Guide", "url": "https://peps.python.org/pep-0008/"}},
    {{"title": "Python List Comprehensions", "url": "https://realpython.com/list-comprehension-python/"}}
  ]
}}
```

IMPORTANT: For suggested_code, always include the complete function definition, not just the changed lines."""
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=0.3,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            result = self._extract_json_from_text(response_text)
            
            if not result:
                # Fallback if JSON parsing fails
                return ReviewComment(
                    original=comment,
                    positive_rephrasing="Let's look at improving this code together.",
                    explanation="I noticed an opportunity to enhance this code. Here's a suggestion:",
                    suggested_code=code_snippet,
                    resources=[
                        {"title": "PEP 8 - Style Guide", "url": "https://peps.python.org/pep-0008/"},
                        {"title": "The Zen of Python", "url": "https://peps.python.org/pep-0020/"}
                    ]
                )
            
            return ReviewComment(
                original=comment,
                positive_rephrasing=result.get("positive_rephrasing", ""),
                explanation=result.get("explanation", ""),
                suggested_code=result.get("suggested_code", ""),
                resources=result.get("resources", [])
            )
            
        except Exception as e:
            print(f"Error generating review: {str(e)}", file=sys.stderr)
            traceback.print_exc()
            return ReviewComment(
                original=comment,
                positive_rephrasing="Let's look at improving this code together.",
                explanation="An error occurred while generating the review. Here's a general suggestion:",
                suggested_code=code_snippet,
                resources=[
                    {"title": "Python Official Documentation", "url": "https://docs.python.org/3/"}
                ]
            )

def process_review_request(request: CodeReviewRequest) -> Dict[str, Any]:
    """Process a code review request and generate empathetic feedback."""
    reviewer = EmpatheticReviewer()
    reviews = []
    
    for comment in request.review_comments:
        review = reviewer.generate_review(request.code_snippet, comment)
        reviews.append(review)
    
    # Generate a summary
    summary = generate_summary(reviews)
    
    return {
        "reviews": [r.model_dump() for r in reviews],
        "summary": summary
    }

def generate_summary(reviews: List[ReviewComment]) -> str:
    """Generate a summary of the code review."""
    if not reviews:
        return "No review comments to summarize."
    
    positive_aspects = [
        "clean and readable",
        "well-structured",
        "efficient",
        "modular",
        "well-documented"
    ]
    
    improvements = len(reviews)
    
    summary = [
        "# Code Review Summary\n",
        f"## Overall Assessment\n",
        f"Your code shows great potential! I've identified {improvements} key areas "
        f"where we can make it even better. The suggested improvements focus on making your code more "
        f"{', '.join(positive_aspects[:2])}, and {positive_aspects[2]}.",
        "\n## Key Recommendations\n"
    ]
    
    for i, review in enumerate(reviews, 1):
        summary.append(f"{i}. {review.positive_rephrasing}")
    
    summary.extend([
        "\n## Next Steps\n",
        "1. Review each suggestion and the reasoning behind it",
        "2. Apply the changes that make sense for your use case",
        "3. Don't hesitate to ask if you'd like more details on any point\n",
        "Remember, code reviews are about learning and improving together. "
        "Every piece of feedback is an opportunity to grow as a developer!"
    ])
    
    return "\n".join(summary)

def generate_markdown_report(reviews: List[Dict[str, Any]], summary: str) -> str:
    """Generate a markdown formatted review report."""
    report = ["# 🚀 Empathetic Code Review Report\n"]
    
    for i, review in enumerate(reviews, 1):
        report.append(f"## 🐍 Analysis of Comment {i}: \"{review['original']}\"\n")
        report.append(f"### 🌟 Positive Rephrasing\n{review['positive_rephrasing']}\n")
        report.append(f"### 💡 The 'Why'\n{review['explanation']}\n")
        
        if review.get('suggested_code'):
            report.append("### ✨ Suggested Improvement\n")
            report.append(f"```python\n{review['suggested_code']}\n```\n")
        
        if review.get('resources'):
            report.append("### 📚 Helpful Resources\n")
            for resource in review['resources']:
                report.append(f"- [{resource['title']}]({resource['url']})")
        
        report.append("\n---\n")
    
    report.append(f"# 📝 Summary\n\n{summary}")
    return '\n'.join(report)

def print_review_report(reviews: List[Dict[str, Any]], summary: str, output_file: str = None, config: Config = None):
    """Print the review report to console and optionally save to a file."""
    config = config or load_config()
    markdown = generate_markdown_report(reviews, summary, config)
    
    # Print to console
    print(markdown)
    
    # Save to file if output_file is provided
    if output_file:
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding='utf-8')
            print(f"\n💾 Report saved to: {output_path.absolute()}")
            
            # Print relative path if possible
            try:
                rel_path = output_path.relative_to(Path.cwd())
                print(f"   (Relative path: {rel_path})")
            except ValueError:
                pass
                
        except Exception as e:
            print(f"\n💡 Could not save report to file: {e}", file=sys.stderr)

def main():
    import argparse
    from datetime import datetime
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Generate empathetic code reviews.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--output', '-o', type=str, 
                      help='Output file path (default: print to console only)', 
                      default=None)
    parser.add_argument('--input', '-i', type=str, 
                      help='Input JSON file (default: use example)', 
                      default=None)
    parser.add_argument('--config', '-c', type=str,
                      help='Path to config file',
                      default='config.json')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config)
        if args.verbose:
            print(f"✅ Loaded configuration from {args.config or 'defaults'}")
    except Exception as e:
        print(f"⚠️  Error loading config: {e}", file=sys.stderr)
        print("⚠️  Using default configuration", file=sys.stderr)
        config = load_config()
    
    # Load request from file or use example
    if args.input and os.path.exists(args.input):
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                request_data = json.load(f)
        except Exception as e:
            print(f"Error loading input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Example usage
        request_data = {
            "code_snippet": "def get_active_users(users):\n    results = []\n    for u in users:\n        if u.is_active == True and u.profile_complete == True:\n            results.append(u)\n    return results",
            "review_comments": [
                "This is inefficient. Don't loop twice conceptually.",
                "Variable 'u' is a bad name.",
                "Boolean comparison '== True' is redundant."
            ]
        }
    
    try:
        if args.verbose:
            print("🔍 Processing review request...")
            
        # Initialize reviewer with config
        reviewer = EmpatheticReviewer(config)
        
        # Process the request
        request = CodeReviewRequest(**request_data)
        result = process_review_request(request, reviewer)
        
        # Generate output filename with timestamp if not provided
        output_file = args.output
        if output_file and output_file.endswith('/'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{output_file}code_review_{timestamp}.md"
        
        # Generate and print/save the report
        if args.verbose:
            print("📊 Generating report...")
            
        print_review_report(
            reviews=result["reviews"],
            summary=result["summary"],
            output_file=output_file,
            config=config
        )
        
        if args.verbose:
            print("✅ Review completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()
