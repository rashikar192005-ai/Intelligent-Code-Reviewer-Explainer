
import ast
import re
import streamlit as st

st.set_page_config(
    page_title="Intelligent Code Reviewer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Intelligent Code Reviewer & Explainer")
st.write(
    "Upload Python, JavaScript, or Java code to identify "
    "possible bugs, understand the code, and view a cleaned version."
)

uploaded_file = st.file_uploader(
    "Upload your code file",
    type=["py", "js", "java"]
)

code = ""

if uploaded_file:
    code = uploaded_file.getvalue().decode("utf-8", errors="replace")
else:
    code = st.text_area(
        "Or paste your code here",
        height=220,
        placeholder="Paste your Python, JavaScript, or Java code..."
    )

def review_code(source, language):
    issues = []
    explanations = []

    lines = source.splitlines()

    if not source.strip():
        return ["No code provided."], "Please upload or paste some code."

    if language == "python":
        try:
            ast.parse(source)
            issues.append("Syntax check: No Python syntax errors detected.")
        except SyntaxError as error:
            issues.append(
                f"Syntax error at line {error.lineno}: {error.msg}"
            )
            explanations.append(
                "Python could not understand this part of the code. "
                "Check the indicated line, indentation, brackets, and colons."
            )

        checks = [
            (r"\beval\s*\(", "Use of eval()",
             "eval() can execute unexpected code. Avoid it with untrusted input."),
            (r"except\s*:", "Bare except statement",
             "A bare except catches many errors and can hide problems. "
             "Catch a specific exception instead."),
            (r"==\s*None\b|\bNone\s*==", "Comparison with None",
             "In Python, use 'is None' instead of '== None'."),
            (r"\bpassword\s*=\s*['\"]|"
             r"\bapi_key\s*=\s*['\"]",
             "Possible hard-coded secret",
             "Do not store passwords or API keys directly in source code.")
        ]

        for pattern, title, explanation in checks:
            if re.search(pattern, source, re.IGNORECASE):
                issues.append("Possible issue: " + title)
                explanations.append(explanation)

        if re.search(r"\bprint\s*\(", source):
            issues.append("Review suggestion: print() statements found.")
            explanations.append(
                "Check whether these print statements are needed "
                "in the final application."
            )

    elif language == "javascript":
        checks = [
            (r"\beval\s*\(", "Use of eval()",
             "eval() can execute unexpected code. Avoid it when possible."),
            (r"\bvar\s+", "Use of var",
             "Consider let or const for clearer variable scope."),
            (r"==(?!=)", "Loose equality operator",
             "Consider === when you need strict equality."),
            (r"\bconsole\.log\s*\(", "Console debugging statement",
             "Remove unnecessary debugging output before release.")
        ]

        for pattern, title, explanation in checks:
            if re.search(pattern, source):
                issues.append("Possible issue: " + title)
                explanations.append(explanation)

        issues.append(
            "Basic pattern review completed; JavaScript syntax "
            "was not fully validated."
        )

    elif language == "java":
        if "System.out.println" in source:
            issues.append("Review suggestion: System.out.println found.")
            explanations.append(
                "Check whether console output is intended for the final program."
            )

        if re.search(r"\bcatch\s*\(\s*Exception\b", source):
            issues.append("Possible issue: Broad exception handling.")
            explanations.append(
                "Catching a specific exception can make errors easier to handle."
            )

        if "TODO" in source:
            issues.append("Review suggestion: TODO comment found.")
            explanations.append(
                "Check whether the unfinished task needs to be completed."
            )

        issues.append(
            "Basic pattern review completed; Java syntax "
            "was not fully validated."
        )

    for number, line in enumerate(lines, start=1):
        if len(line) > 100:
            issues.append(
                f"Style suggestion: Line {number} exceeds 100 characters."
            )

    if not explanations:
        explanations.append(
            "No issues were identified by the basic checks. "
            "This does not guarantee that the program is bug-free."
        )

    return issues, "\n\n".join(explanations)


if st.button("🔎 Review My Code", type="primary"):
    if not code.strip():
        st.warning("Please upload or paste a code file first.")
    else:
        extension = (
            uploaded_file.name.rsplit(".", 1)[-1].lower()
            if uploaded_file
            else "python"
        )

        language = {
            "py": "python",
            "python": "python",
            "js": "javascript",
            "java": "java"
        }.get(extension, "python")

        issues, explanation = review_code(code, language)

        # Clean trailing spaces without changing program logic.
        cleaned_code = "\n".join(
            line.rstrip() for line in code.splitlines()
        ).strip()

        st.subheader("1. Bug Report")
        for issue in issues:
            st.write("- " + issue)

        st.subheader("2. Plain-Language Explanation")
        st.write(explanation)

        st.subheader("3. Cleaned Code Preview")
        st.caption(
            "This preview removes extra whitespace. "
            "It is not an automatic AI refactor."
        )
        st.code(cleaned_code, language=language)

        st.download_button(
            "Download Reviewed Code",
            data=cleaned_code,
            file_name=f"reviewed_code.{extension if extension != 'python' else 'py'}",
            mime="text/plain"
        )

        st.success("Code review completed!")
        st.info(
            "This version uses rule-based static checks. "
            "It does not use an external AI model."
        )
