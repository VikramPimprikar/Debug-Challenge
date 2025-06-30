## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# Assuming crewai_tools and its dependencies are installed
# If PDFLoader is part of crewai_tools, it should be imported from there.
# If not, you might need to install and import from a library like langchain.document_loaders
# For this correction, I'll assume it's a separate import if not directly from crewai_tools.
try:
    from crewai_tools import SerperDevTool # Direct import if available
    # If PDFLoader is also directly under crewai_tools or crewai_tools.tools
    # from crewai_tools.tools.pdf_loader_tool import PDFLoader as PDFLoaderTool # Example if it exists
except ImportError:
    print("crewai_tools or its specific components not found. Ensure it's installed correctly.")
    # Fallback or alternative imports if crewai_tools doesn't provide them
    # For PDF loading, a common library is langchain
    try:
        from langchain_community.document_loaders import PyPDFLoader as PDFLoader
    except ImportError:
        print("PyPDFLoader from langchain_community not found. Please install it: pip install langchain-community pypdf")
        PDFLoader = None # Set to None to indicate it's not available


## Creating search tool
# No change needed here if SerperDevTool is imported correctly
search_tool = SerperDevTool()

## Creating custom pdf reader tool
# CrewAI tools often expect a specific structure, usually inheriting from BaseTool or using tool decorator.
# For simplicity and to fix the immediate issues, I'll make it a standard class with a method.
# To make it a proper CrewAI tool, you'd typically subclass `BaseTool` and define `_run`.
# For the purpose of correcting the function, I'll make it a regular async method.

class BloodTestReportTool:
    # It's better to pass the loader instance or ensure PDFLoader is robustly imported
    # and handle potential file not found errors.
    
    @staticmethod # Use staticmethod if it doesn't need 'self'
    async def read_data_tool(path: str = 'data/sample.pdf') -> str:
        """Tool to read data from a pdf file from a path

        Args:
            path (str, optional): Path of the pdf file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full Blood Test report file
        """
        if not PDFLoader:
            return "Error: PDFLoader is not available. Please install necessary libraries."

        if not os.path.exists(path):
            return f"Error: File not found at path: {path}"

        try:
            docs = PDFLoader(file_path=path).load()
        except Exception as e:
            return f"Error loading PDF from {path}: {e}"

        full_report = ""
        for data in docs:
            # Clean and format the report data
            content = data.page_content
            
            # Remove extra whitespaces and format properly
            # Using regex for more efficient whitespace handling
            import re
            content = re.sub(r'\s+', ' ', content).strip() # Replace multiple whitespaces with single space and strip
            content = content.replace(" \n", "\n").replace("\n ", "\n") # Handle spaces around newlines
            
            full_report += content + "\n"
            
        return full_report

## Creating Nutrition Analysis Tool
class NutritionTool:
    # Corrected method signature and example of where to add analysis logic.
    @staticmethod
    async def analyze_nutrition_tool(blood_report_data: str) -> str:
        """Analyzes the provided blood report data for nutritional insights.

        Args:
            blood_report_data (str): The raw text data from the blood test report.

        Returns:
            str: A string containing the nutritional analysis.
        """
        if not isinstance(blood_report_data, str):
            return "Error: Input blood_report_data must be a string."

        # Process and analyze the blood report data
        processed_data = blood_report_data
        
        # Clean up the data format - this cleaning might be better done in read_data_tool
        # but if needed here, a more robust method like regex is better.
        import re
        processed_data = re.sub(r' {2,}', ' ', processed_data) # Replace two or more spaces with a single space
        processed_data = processed_data.strip() # Remove leading/trailing whitespace

        # TODO: Implement actual nutrition analysis logic here.
        # This would involve parsing the processed_data to extract specific
        # blood markers (e.g., hemoglobin, cholesterol, glucose levels)
        # and then mapping them to nutritional deficiencies or recommendations.
        # Example:
        # if "Hemoglobin: 10.0" in processed_data:
        #     analysis_result = "Low Hemoglobin detected, consider iron-rich foods."
        # else:
        #     analysis_result = "Basic nutritional analysis based on report: " + processed_data[:100] + "..." # Truncate for example
        
        return f"Nutrition analysis functionality to be implemented. Processed data snippet: {processed_data[:200]}..." # Returning a snippet for demonstration

## Creating Exercise Planning Tool
class ExerciseTool:
    # Corrected method signature and example of where to add planning logic.
    @staticmethod
    async def create_exercise_plan_tool(blood_report_data: str) -> str:
        """Creates an exercise plan based on the blood report data.

        Args:
            blood_report_data (str): The raw text data from the blood test report.

        Returns:
            str: A string containing the exercise plan.
        """
        if not isinstance(blood_report_data, str):
            return "Error: Input blood_report_data must be a string."

        # TODO: Implement exercise planning logic here.
        # This would involve parsing the blood report for indicators of
        # physical condition, potential risks (e.g., high cholesterol,
        # issues with blood pressure, energy levels), and then generating
        # a suitable exercise routine.
        # Example:
        # if "Cholesterol: High" in blood_report_data:
        #     exercise_plan = "Focus on cardiovascular exercises (e.g., brisk walking, jogging) for 30 mins, 5 times a week."
        # else:
        #     exercise_plan = "General exercise recommendation: daily moderate activity."

        return f"Exercise planning functionality to be implemented. Received data snippet: {blood_report_data[:200]}..." # Returning a snippet for demonstration

# Example of how you might use these tools (for testing purposes)
async def main():
    # Make sure you have a 'data' directory with a 'sample.pdf' for testing
    # Or change the path to an existing PDF for your tests.
    pdf_report = await BloodTestReportTool.read_data_tool(path='data/sample.pdf')
    print("\n--- PDF Report ---")
    print(pdf_report)

    nutrition_analysis = await NutritionTool.analyze_nutrition_tool(pdf_report)
    print("\n--- Nutrition Analysis ---")
    print(nutrition_analysis)

    exercise_plan = await ExerciseTool.create_exercise_plan_tool(pdf_report)
    print("\n--- Exercise Plan ---")
    print(exercise_plan)

if __name__ == "__main__":
    import asyncio
    # To run the async main function
    # Ensure you have 'data/sample.pdf' or change the path in main()
    asyncio.run(main())