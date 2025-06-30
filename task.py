# Importing libraries and files
from crewai import Task
# Assuming 'doctor' and 'verifier' are instances of Agent defined elsewhere, e.g., in agents.py
# from agents import doctor, verifier

# Assuming 'search_tool' is an instance of SerperDevTool, imported correctly.
# And assuming your BloodTestReportTool class is defined and imported as well.
# from tools import search_tool, BloodTestReportTool

# Placeholder for agents and tools for demonstration if not defined elsewhere
# You would replace these with your actual agent and tool instances
class MockAgent:
    def __init__(self, role, goal, backstory):
        self.role = role
        self.goal = goal
        self.backstory = backstory
    def __str__(self):
        return f"Agent(role={self.role})"

class MockSearchTool:
    def run(self, query: str):
        return f"Mock search result for: {query}"

class MockBloodTestReportTool:
    @staticmethod
    async def read_data_tool(path: str = 'data/sample.pdf') -> str:
        # This should ideally read a real PDF for actual use
        print(f"Mocking reading data from: {path}")
        return "Mock Blood Test Report Data: Hemoglobin: 14.0, Glucose: 90 mg/dL"

class MockNutritionTool:
    @staticmethod
    async def analyze_nutrition_tool(blood_report_data: str) -> str:
        print(f"Mocking nutrition analysis for: {blood_report_data[:50]}...")
        return "Mock Nutrition Analysis: Healthy"

class MockExerciseTool:
    @staticmethod
    async def create_exercise_plan_tool(blood_report_data: str) -> str:
        print(f"Mocking exercise plan for: {blood_report_data[:50]}...")
        return "Mock Exercise Plan: Daily 30 min walk"

# Instantiate your actual agents and tools here
doctor = MockAgent(role="Medical Doctor", goal="Provide health insights", backstory="...")
verifier = MockAgent(role="File Verifier", goal="Verify file authenticity", backstory="...")
search_tool = MockSearchTool()
# IMPORTANT: For crewAI to recognize a method as a tool, it's often better to wrap it
# as a BaseTool or pass the class itself if it has a __call__ method or the method is
# designed to be directly called by the agent.
# If BloodTestReportTool is a custom tool wrapper (e.g., inheriting from BaseTool),
# then you'd pass an instance of that tool.
# If you want to use the static method directly, CrewAI might need a small wrapper.

# For simpler cases, you can sometimes pass the class reference for crewai to instantiate
# or, if it's a standalone function, pass the function.

# Let's assume for a moment that BloodTestReportTool itself is designed to be a tool
# or we need to pass a specific callable.

# Re-importing your actual tools (assuming they are defined as in your previous solution)
# from tools import BloodTestReportTool # This is the class
from crewai_tools import tool # Import the tool decorator if using standalone functions

# If you want to explicitly define the read_data_tool as a CrewAI @tool
# (This is a common and robust way to make a standalone function available as a tool)
@tool("Blood Test Report Reader")
def read_blood_test_report(path: str = 'data/sample.pdf') -> str:
    """Reads data from a PDF blood test report file.
    Args:
        path (str, optional): Path of the PDF file. Defaults to 'data/sample.pdf'.
    Returns:
        str: Full Blood Test report file content.
    """
    # This function would internally call your BloodTestReportTool.read_data_tool
    # or contain its logic. For demonstration, I'll use the mock.
    return MockBloodTestReportTool.read_data_tool(path)

@tool("Nutrition Analysis Tool")
def analyze_nutrition(blood_report_data: str) -> str:
    """Analyzes blood test report data to provide nutritional insights."""
    return MockNutritionTool.analyze_nutrition_tool(blood_report_data)

@tool("Exercise Planning Tool")
def create_exercise_plan(blood_report_data: str) -> str:
    """Creates an exercise plan based on blood report data."""
    return MockExerciseTool.create_exercise_plan_tool(blood_report_data)

# Now, use these `@tool` decorated functions in your tasks.

# Task 1: General Health Analysis Task
help_patients = Task(
    description=(
        "Analyze the user's blood test report and provide a medically accurate summary. "
        "Highlight any abnormalities, explain what they could indicate, and recommend "
        "next steps for follow-up. Ensure the analysis is user-friendly and backed by science."
    ),
    expected_output=(
        "A structured report with:\n"
        "- Key normal and abnormal findings\n"
        "- Possible related conditions (clearly marked as suggestions, not diagnoses)\n"
        "- Suggested follow-ups or lifestyle changes\n"
        "- Optional links to credible sources like WebMD, Mayo Clinic, etc."
    ),
    agent=doctor,
    # Use the @tool decorated function directly
    tools=[read_blood_test_report, search_tool],
    async_execution=False,
)

# Task 2: Nutrition Analysis Based on Blood Report
nutrition_analysis = Task(
    description=(
        "Analyze the blood test report to provide nutrition advice. "
        "Focus on vitamin deficiencies, cholesterol levels, glucose, and other markers. "
        "Recommend appropriate dietary changes or supplements based on standard guidelines."
    ),
    expected_output=(
        "A personalized nutrition report with:\n"
        "- Diet changes based on markers (e.g., iron, B12, glucose)\n"
        "- Supplement suggestions (if necessary)\n"
        "- Foods to include or avoid\n"
        "- Optional reference to WHO/NIH guidelines"
    ),
    agent=doctor,
    # Here, the agent will first need to read the report, then pass it to the nutrition analysis tool.
    # CrewAI handles the chaining if the description and tools allow.
    # The agent's reasoning will determine the flow.
    tools=[read_blood_test_report, analyze_nutrition],
    async_execution=False,
)

# Task 3: Exercise Planning Task
exercise_planning = Task(
    description=(
        "Based on the patient's blood test and overall health markers, "
        "create a safe and personalized exercise plan. "
        "Consider factors like anemia, cholesterol, blood sugar, and overall fitness."
    ),
    expected_output=(
        "A health-aware workout plan including:\n"
        "- Recommended activities (cardio, strength, flexibility)\n"
        "- Weekly frequency and intensity levels\n"
        "- Warnings or exclusions if any blood indicators suggest risk\n"
        "- Tips for tracking progress safely"
    ),
    agent=doctor,
    tools=[read_blood_test_report, create_exercise_plan],
    async_execution=False,
)

# Task 4: File Type Verification Task
verification = Task(
    description=(
        "Determine whether the uploaded file is a valid blood test report. "
        "Analyze structure, keywords, and values to verify its authenticity. "
        "Flag any issues or mismatches in expected format."
    ),
    expected_output=(
        "A verification result indicating:\n"
        "- Whether the file is a valid blood test report\n"
        "- Any missing or malformed data\n"
        "- Suggestions for accepted formats (if rejected)"
    ),
    agent=verifier,
    tools=[read_blood_test_report], # The verifier also needs to read the data to verify it.
    async_execution=False,
)

# Example of how you might combine them in a Crew (conceptual)
# from crewai import Crew
#
# crew = Crew(
#     agents=[doctor, verifier],
#     tasks=[help_patients, nutrition_analysis, exercise_planning, verification],
#     verbose=True
# )
#
# # To run the crew, you would typically have an input for the tasks.
# # For the BloodTestReportTool, you'd need to ensure the `path` is handled.
# # This often involves a preliminary task or explicit input to the crew.
# # For instance:
# # result = crew.kickoff(inputs={'pdf_path': 'data/sample.pdf'})
# # print(result)