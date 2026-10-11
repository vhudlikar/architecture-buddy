import html
import json
import time

import ollama
import streamlit as st


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Architecture Buddy AI",
    page_icon="🏗️",
    layout="wide"
)


# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "elapsed" not in st.session_state:
    st.session_state.elapsed = 0

if "code_input" not in st.session_state:
    st.session_state.code_input = ""

if "sample_type" not in st.session_state:
    st.session_state.sample_type = "None"


# --------------------------------------------------
# SAMPLE CODE
# --------------------------------------------------

SAMPLE_CODE = {
    "ServiceNow GlideRecord": """var gr = new GlideRecord('incident');

gr.addActiveQuery();
gr.addQuery('priority', 1);
gr.query();

while (gr.next()) {
    gs.info(
        gr.number + ' - ' +
        gr.short_description
    );

    if (gr.assigned_to.nil()) {
        gr.work_notes =
            'Auto review detected unassigned incident';

        gr.update();
    }
}""",

    "Python Function": """def calculate_total(price, qty):
    if qty <= 0:
        raise ValueError("Quantity must be positive")

    return price * qty

amount = calculate_total(100, 5)
print(amount)
""",

    "REST API": """import requests

def get_user(user_id):
    response = requests.get(
        f"https://api.company.com/users/{user_id}",
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None
"""
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def load_selected_sample():
    selected_sample = st.session_state.sample_type

    if selected_sample in SAMPLE_CODE:
        st.session_state.code_input = SAMPLE_CODE[selected_sample]
        st.session_state.analysis = None
        st.session_state.elapsed = 0


def clear_application():
    st.session_state.analysis = None
    st.session_state.elapsed = 0
    st.session_state.code_input = ""
    st.session_state.sample_type = "None"


def normalize_list(value):
    """
    Ensures that a returned JSON value is always handled
    as a clean Python list.
    """

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def display_bullet_list(items, empty_message):
    normalized_items = normalize_list(items)

    if not normalized_items:
        st.write(empty_message)
        return

    for item in normalized_items:
        st.markdown(f"- {item}")


def create_download_report(analysis, elapsed):
    """
    Converts the structured JSON analysis into
    a readable Markdown report.
    """

    ratings = analysis.get("ratings", {})

    report_lines = [
        "# Architecture Buddy AI Report",
        "",
        f"Analysis completed in {elapsed} seconds.",
        "",
        "## Executive Summary",
        "",
        analysis.get(
            "executive_summary",
            "No executive summary was generated."
        ),
        "",
        "## Purpose",
        "",
        analysis.get(
            "purpose",
            "No purpose was generated."
        ),
        "",
        "## Detected Technology",
        "",
        analysis.get(
            "detected_technology",
            "Not identified"
        ),
        "",
        "## Key Components",
        ""
    ]

    for component in normalize_list(
        analysis.get("key_components", [])
    ):
        report_lines.append(f"- {component}")

    report_lines.extend([
        "",
        "## Architecture Review",
        ""
    ])

    for observation in normalize_list(
        analysis.get("architecture_review", [])
    ):
        report_lines.append(f"- {observation}")

    report_lines.extend([
        "",
        "## Assessment",
        "",
        f"- Complexity: {ratings.get('complexity', 'N/A')}",
        f"- Maintainability: "
        f"{ratings.get('maintainability', 'N/A')}",
        f"- Security: {ratings.get('security', 'N/A')}",
        "",
        "## Risks",
        ""
    ])

    for risk in normalize_list(
        analysis.get("risks", [])
    ):
        report_lines.append(f"- {risk}")

    report_lines.extend([
        "",
        "## Improvements",
        ""
    ])

    for improvement in normalize_list(
        analysis.get("improvements", [])
    ):
        report_lines.append(f"- {improvement}")

    report_lines.extend([
        "",
        "## Architecture Flow",
        ""
    ])

    flow_steps = normalize_list(
        analysis.get("architecture_flow", [])
    )

    for index, step in enumerate(flow_steps):
        report_lines.append(step)

        if index < len(flow_steps) - 1:
            report_lines.append("↓")

    return "\n".join(report_lines)


def render_architecture_flow(flow_steps):
    """
    Streamlit renders the diagram instead of allowing
    the AI model to control its formatting.
    """

    normalized_steps = normalize_list(flow_steps)

    if not normalized_steps:
        st.info("No architecture flow was generated.")
        return

    for index, step in enumerate(normalized_steps):
        safe_step = html.escape(step)

        st.markdown(
            f"""
            <div style="
                max-width: 700px;
                margin: 5px auto;
                padding: 14px 18px;
                text-align: center;
                background-color: #17202A;
                border: 1px solid #3D566E;
                border-radius: 10px;
                font-weight: 600;
                color: #FFFFFF;
            ">
                {safe_step}
            </div>
            """,
            unsafe_allow_html=True
        )

        if index < len(normalized_steps) - 1:
            st.markdown(
                """
                <div style="
                    text-align: center;
                    font-size: 27px;
                    line-height: 30px;
                    color: #7FDBFF;
                ">
                    ↓
                </div>
                """,
                unsafe_allow_html=True
            )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🏗️ Architecture Buddy AI")

st.caption(
    "AI-Powered Architecture Review Assistant "
    "for Developers and Architects"
)

st.info(
    "✅ 100% Local AI | "
    "✅ Open Source | "
    "✅ Powered by Ollama + Llama 3.2 | "
    "✅ No Data Leaves Your Device"
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("About")

    st.write(
        """
Architecture Buddy AI helps developers and architects:

- Understand unfamiliar code
- Generate executive summaries
- Review architecture
- Identify risks
- Suggest improvements
- Create architecture documentation

**Powered by:**

- Streamlit
- Ollama
- Llama 3.2
"""
    )

    st.divider()

    st.selectbox(
        "Choose Sample Code",
        [
            "None",
            "ServiceNow GlideRecord",
            "Python Function",
            "REST API"
        ],
        key="sample_type"
    )

    st.button(
        "📌 Load Selected Sample",
        on_click=load_selected_sample,
        use_container_width=True
    )


# --------------------------------------------------
# CODE INPUT
# --------------------------------------------------

st.text_area(
    "Paste your code here",
    key="code_input",
    height=350,
    placeholder=(
        "Paste ServiceNow, Python, JavaScript, "
        "REST API, or other source code here..."
    )
)


# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------

button_column_1, button_column_2 = st.columns(2)

with button_column_1:
    analyze_clicked = st.button(
        "🔍 Analyze Architecture",
        type="primary",
        use_container_width=True
    )

with button_column_2:
    st.button(
        "🗑 Clear Results",
        on_click=clear_application,
        use_container_width=True
    )


# --------------------------------------------------
# ANALYSIS
# --------------------------------------------------

if analyze_clicked:
    code_input = st.session_state.code_input.strip()

    if not code_input:
        st.warning(
            "Please paste code or load a sample first."
        )
        st.stop()

    prompt = f"""
You are a Principal Software Architect with expertise in
ServiceNow, Python, JavaScript, REST APIs, security,
performance, maintainability and enterprise architecture.

Analyze only the supplied code.

GENERAL RULES

1. Base every observation on evidence visible in the code.
2. Do not invent technologies, infrastructure, integrations,
   databases or business requirements.
3. Do not repeat or paste the supplied source code.
4. Do not provide a line-by-line code explanation.
5. Use concise, professional and business-friendly language.
6. Return only valid JSON.
7. Do not wrap the JSON in Markdown or triple backticks.

TECHNOLOGY DETECTION

1. Identify the technology from evidence in the code.
2. If ServiceNow code is detected, use ServiceNow terminology.
3. Recognize ServiceNow patterns including:
   - GlideRecord
   - GlideAggregate
   - GlideSystem and gs
   - Business Rules
   - Script Includes
   - Client Scripts
   - UI Actions
   - Flow Designer
   - Scheduled Jobs
   - Scripted REST APIs
   - Transform Maps
4. Never mention Salesforce, Apex, SOQL or Salesforce Database
   unless those technologies explicitly appear in the code.

ARCHITECTURE REVIEW

Return between 3 and 5 architecture observations.

The architecture review must explain:

1. The data source or external service being accessed.
2. The filtering or query behavior.
3. The main processing and decision points.
4. Any record updates, responses or side effects.
5. Relevant performance, maintainability, scalability or
   security considerations.

Do not return source code inside the architecture review.

ASSESSMENT RATINGS

Return only Low, Medium or High.

Complexity:
- Low means the code has simple execution logic.
- Medium means the code has multiple operations or decisions.
- High means the code has complex dependencies or branching.

Maintainability:
- High means the code is clear, reusable and easy to maintain.
- Medium means the code is acceptable but needs improvements.
- Low means the code is difficult or risky to maintain.

Security:
- High means no meaningful security concern is visible.
- Medium means some safeguards or validation are missing.
- Low means significant security concerns are visible.

RISKS AND IMPROVEMENTS

1. Return between 3 and 5 practical risks.
2. Return between 3 and 5 practical improvements.
3. Each risk must be supported by visible code behavior.
4. Each improvement must be technology-specific.
5. For ServiceNow code, follow ServiceNow best practices.
6. Do not recommend unrelated frameworks.
7. Do not invent errors that are not supported by the code.

ARCHITECTURE FLOW

Return between 4 and 8 architecture flow steps.

Each flow step must:

1. Describe an action actually performed by the code.
2. Use short, business-friendly wording.
3. Contain no arrows, brackets, pipes or numbering.
4. Contain no Markdown.
5. Not use generic labels such as:
   Input, Validation, Business Logic, Processing or Output.

For ServiceNow GlideRecord code, valid step wording could be:

- Initialize Incident Query
- Apply Active Record Filter
- Apply Priority Filter
- Execute Incident Query
- Iterate Through Matching Incidents
- Check Assignment Status
- Update Work Notes
- Log Incident Details

Use only steps that match the supplied code.

Return JSON using exactly this structure:

{{
  "detected_technology": "Detected technology",
  "executive_summary": "Concise executive summary",
  "purpose": "Purpose of the code",
  "key_components": [
    "Component 1",
    "Component 2",
    "Component 3"
  ],
  "architecture_review": [
    "Architecture observation 1",
    "Architecture observation 2",
    "Architecture observation 3"
  ],
  "ratings": {{
    "complexity": "Low",
    "maintainability": "Medium",
    "security": "Medium"
  }},
  "risks": [
    "Risk 1",
    "Risk 2",
    "Risk 3"
  ],
  "improvements": [
    "Improvement 1",
    "Improvement 2",
    "Improvement 3"
  ],
  "architecture_flow": [
    "Specific first step",
    "Specific second step",
    "Specific third step",
    "Specific final step"
  ]
}}

SUPPLIED CODE:

{code_input}
"""

    with st.spinner(
        "Reviewing architecture with local AI..."
    ):
        start_time = time.time()

        try:
            response = ollama.chat(
                model="llama3.2",
                format="json",
                options={
                    "temperature": 0.1
                },
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            raw_response = response["message"]["content"]

            analysis = json.loads(raw_response)

            required_fields = [
                "detected_technology",
                "executive_summary",
                "purpose",
                "key_components",
                "architecture_review",
                "ratings",
                "risks",
                "improvements",
                "architecture_flow"
            ]

            missing_fields = [
                field
                for field in required_fields
                if field not in analysis
            ]

            if missing_fields:
                raise ValueError(
                    "The model response is missing: "
                    + ", ".join(missing_fields)
                )

            st.session_state.analysis = analysis

            st.session_state.elapsed = round(
                time.time() - start_time,
                2
            )

        except json.JSONDecodeError:
            st.error(
                "The local model returned an invalid response. "
                "Please click Analyze Architecture again."
            )

        except Exception as error:
            st.error(
                f"Analysis failed: {error}"
            )


# --------------------------------------------------
# DISPLAY REPORT
# --------------------------------------------------

if st.session_state.analysis:
    analysis = st.session_state.analysis

    st.success(
        "✅ Analysis completed in "
        f"{st.session_state.elapsed} seconds"
    )

    st.markdown("## Executive Summary")

    st.write(
        analysis.get(
            "executive_summary",
            "No executive summary was generated."
        )
    )

    st.markdown("## Purpose")

    st.write(
        analysis.get(
            "purpose",
            "No purpose was generated."
        )
    )

    st.markdown("## Detected Technology")

    st.write(
        analysis.get(
            "detected_technology",
            "Not identified"
        )
    )

    st.markdown("## Key Components")

    display_bullet_list(
        analysis.get("key_components", []),
        "No key components were identified."
    )

    st.markdown("## Architecture Review")

    display_bullet_list(
        analysis.get("architecture_review", []),
        "No architecture observations were generated."
    )

    st.markdown("## Assessment")

    ratings = analysis.get("ratings", {})

    rating_column_1, rating_column_2, rating_column_3 = (
        st.columns(3)
    )

    with rating_column_1:
        st.metric(
            "Complexity",
            ratings.get("complexity", "N/A")
        )

    with rating_column_2:
        st.metric(
            "Maintainability",
            ratings.get("maintainability", "N/A")
        )

    with rating_column_3:
        st.metric(
            "Security",
            ratings.get("security", "N/A")
        )

    st.markdown("## Risks")

    display_bullet_list(
        analysis.get("risks", []),
        "No significant risks were identified."
    )

    st.markdown("## Improvements")

    display_bullet_list(
        analysis.get("improvements", []),
        "No improvements were generated."
    )

    st.markdown("## Architecture Flow")

    render_architecture_flow(
        analysis.get("architecture_flow", [])
    )

    markdown_report = create_download_report(
        analysis,
        st.session_state.elapsed
    )

    st.download_button(
        label="📄 Download Report",
        data=markdown_report,
        file_name="architecture_review.md",
        mime="text/markdown"
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.caption(
    "Built with Streamlit + Ollama + Llama 3.2"
)