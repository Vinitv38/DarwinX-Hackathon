import json
import os
import sys
from typing import List, Dict, Any
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ReviewComment(BaseModel):
    original: str
    positive_rephrasing: str
    explanation: str
    suggested_code: str
    resources: List[Dict[str, str]]

class CodeReviewRequest(BaseModel):
    code_snippet: str
    review_comments: List[str]

class EmpatheticReviewer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-70b-8192"
    
    def generate_review(self, code_snippet: str, comment: str) -> Dict[str, Any]:
        """Generate an empathetic code review using Groq's API."""
        system_prompt = """You are an experienced senior developer providing a code review. 
        Your goal is to transform critical comments into constructive, educational feedback.
        
        For each comment, provide:
        1. A positive rephrasing
        2. Explanation of why this is important
        3. Suggested code improvement
        4. Helpful resources (if applicable)
        
        Be empathetic and educational in your responses.
        """
        
        user_prompt = f"""Code to review:
```python
{code_snippet}
```

Review comment: "{comment}"

Please provide a constructive review response in JSON format with these keys:
- positive_rephrasing: A gentle and encouraging version of the feedback
- explanation: Clear explanation of the underlying software principle
- suggested_code: The improved code snippet
- resources: List of helpful resources with title and URL
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            review_data = json.loads(response.choices[0].message.content)
            
            return {
                "original": comment,
                "positive_rephrasing": review_data.get("positive_rephrasing", ""),
                "explanation": review_data.get("explanation", ""),
                "suggested_code": review_data.get("suggested_code", ""),
                "resources": review_data.get("resources", [])
            }
            
        except Exception as e:
            print(f"Error generating review: {str(e)}")
            return {
                "original": comment,
                "positive_rephrasing": "I noticed something we can improve in the code.",
                "explanation": "There was an error generating the review.",
                "suggested_code": "",
                "resources": []
            }

def process_review_request(request: CodeReviewRequest) -> Dict[str, Any]:
    """Process a code review request and generate empathetic feedback."""
    reviewer = EmpatheticReviewer()
    reviews = []
    
    for comment in request.review_comments:
        review = reviewer.generate_review(request.code_snippet, comment)
        reviews.append(review)
    
    return {"reviews": reviews, "summary": generate_summary(reviews)}

def generate_summary(reviews: List[Dict[str, Any]]) -> str:
    """Generate an encouraging and comprehensive summary of the code review."""
    if not reviews:
        return "No review comments to summarize."
    
    # Count the number of suggestions
    num_suggestions = len(reviews)
    
    # Identify common themes
    themes = set()
    for review in reviews:
        if 'input' in review['original'].lower() or 'validation' in review['original'].lower():
            themes.add("input validation")
        if 'docstring' in review['original'].lower() or 'documentation' in review['original'].lower():
            themes.add("code documentation")
        if 'edge case' in review['original'].lower() or 'robust' in review['original'].lower():
            themes.add("robustness")
    
    themes_list = ", ".join(f"**{theme}**" for theme in sorted(themes)) if themes else "code quality"
    
    summary = [
        "# 📝 Code Review Summary\n",
        "## 🌟 Overall Assessment\n",
        f"Great job on your code! I've reviewed it and found {num_suggestions} areas where we can make it even better. "
        f"The suggestions focus on improving {themes_list}, which will help make your code more maintainable and robust.\n",
        "## 🔍 Key Recommendations\n"
    ]
    
    # Add each recommendation with a positive spin
    for i, review in enumerate(reviews, 1):
        if review['positive_rephrasing']:
            summary.append(f"{i}. {review['positive_rephrasing']}")
    
    # Add encouraging next steps
    summary.extend([
        "\n## 🚀 Next Steps\n",
        "1. **Review** each suggestion and the reasoning behind it - every improvement makes your code stronger!",
        "2. **Implement** the changes that align with your project's needs",
        "3. **Celebrate** these learning opportunities - they're signs of growth as a developer",
        "4. **Reach out** if you'd like to discuss any of these suggestions in more detail\n",
        "## 💫 Final Thoughts\n",
        "Remember, code reviews are about learning and growing together. The fact that you're open to feedback "
        "shows your commitment to writing great code. Keep up the fantastic work, and know that each improvement "
        "you make helps build your skills and makes our codebase even better! 🎉"
    ])
    
    return "\n".join(summary)

def generate_markdown_report(reviews: List[Dict[str, Any]], summary: str) -> str:
    """Generate a markdown formatted review report."""
    report = ["# 🚀 Empathetic Code Review Report\n"]
    
    for i, review in enumerate(reviews, 1):
        report.extend([
            f"## Analysis of Comment {i}: \"{review['original']}\"\n",
            f"**Positive Rephrasing:** {review['positive_rephrasing']}\n",
            f"**The 'Why':** {review['explanation']}\n"
        ])
        
        if review['suggested_code']:
            report.append(f"**Suggested Improvement:**\n```python\n{review['suggested_code']}\n```\n")
        
        if review['resources']:
            report.append("**Helpful Resources:**\n")
            for resource in review['resources']:
                report.append(f"- [{resource['title']}]({resource['url']})")
            report.append("")
        
        report.append("---\n")
    
    report.append(summary)
    return "\n".join(report)

def load_request_from_file(file_path: str) -> dict:
    """Load review request from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading input file: {str(e)}")
        sys.exit(1)

def main():
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate empathetic code reviews')
    parser.add_argument('-i', '--input', help='Input JSON file with code and comments')
    parser.add_argument('-o', '--output', default='code_review.md', 
                       help='Output file path (default: code_review.md)')
    
    args = parser.parse_args()
    
    # Load request from file or use default example
    if args.input:
        request_data = load_request_from_file(args.input)
    else:
        # Default example
        request_data = {
            "code_snippet": "def get_active_users(users):\n    results = []\n    for u in users:\n        if u.is_active == True and u.profile_complete == True:\n            results.append(u)\n    return results",
            "review_comments": [
                "This is inefficient. Don't loop twice conceptually.",
                "Variable 'u' is a bad name.",
                "Boolean comparison '== True' is redundant."
            ]
        }
    
    try:
        # Process the request
        request = CodeReviewRequest(**request_data)
        result = process_review_request(request)
        
        # Generate the report
        markdown = generate_markdown_report(result["reviews"], result["summary"])
        
        # Print to console
        print("\n" + "="*80)
        print("📝 CODE REVIEW REPORT")
        print("="*80 + "\n")
        print(markdown)
        
        # Save to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n✅ Report saved to {os.path.abspath(args.output)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
