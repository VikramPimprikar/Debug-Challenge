from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio # Import asyncio for running async functions if needed in tools

# CrewAI imports
from crewai import Crew, Process # Corrected: Import Crew and Process
# Assuming 'doctor' agent is correctly defined in agents.py
# and 'help_patients' task is correctly defined in task.py
# Make sure these files are structured to expose these objects directly.
from agents import doctor
from task import help_patients
# You also need to ensure the @tool decorated functions (like read_blood_test_report)
# are accessible, either by importing them directly if they are in your 'tools.py'
# and marked with @tool, or by ensuring the agent's setup correctly accesses them.
# For simplicity, assuming the @tool functions are available via the agent's tools.

app = FastAPI(title="Blood Test Report Analyser")

def run_crew(query: str, file_path: str): # file_path is now mandatory
    """To run the whole crew"""
    
    # IMPORTANT: Modify the task description to explicitly mention the file path,
    # or ensure your agent is smart enough to infer it from the context
    # and use the read_blood_test_report tool with this path.
    # A common pattern is to make the task description dynamic based on inputs.
    
    # Here's one way to make the task explicitly aware of the file_path:
    # We create a new task instance for each run to ensure it uses the specific file_path.
    # Alternatively, ensure your agents' `goal` or `backstory`
    # guides them to use the tool with available context.
    
    # A robust way is to pass the file_path as part of the task's context,
    # and the agent uses it when it decides to call the tool.
    # The agent will look at its tools and the task description/context.
    # If `read_blood_test_report` is given to the agent, and the task needs
    # to process a file, the agent should ideally pick it up.
    
    # Let's ensure the `help_patients` task is correctly configured to use
    # the file path when calling `read_blood_test_report`.
    # Your `read_blood_test_report` function (from tools.py)
    # should be designed to take a `path` argument.
    
    # The `help_patients` task description should implicitly guide the agent
    # to use the `read_blood_test_report` tool with the provided file.
    # The `kickoff` inputs are available to the entire crew and its agents/tasks.
    # The agent's reasoning will link 'file_path' from `inputs` to the `path` argument of `read_blood_test_report`.
    
    medical_crew = Crew(
        agents=[doctor],
        tasks=[help_patients],
        process=Process.sequential,
        verbose=True # It's good to have verbose output for debugging CrewAI runs
    )

    # Pass both query and file_path to the crew's kickoff method.
    # The agents, guided by their roles and task descriptions, will access these inputs.
    result = medical_crew.kickoff({'query': query, 'file_path': file_path})
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Summarise my Blood Test Report")
):
    """Analyze blood test report and provide comprehensive health recommendations"""

    # Generate a unique filename to avoid conflicts, including original extension
    file_extension = os.path.splitext(file.filename)[1]
    if not file_extension: # Ensure there's an extension
        file_extension = ".pdf" # Default to PDF if no extension provided
    
    file_id = str(uuid.uuid4())
    file_path = os.path.join("data", f"blood_test_report_{file_id}{file_extension}")

    try:
        os.makedirs("data", exist_ok=True)

        # Write the uploaded file content to the new path
        # Use await with file.read() as it's an async operation
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Ensure query is not empty if it's passed as Form data
        if not query.strip(): # Use .strip() to handle whitespace-only strings
            query = "Summarise my Blood Test Report"

        # Now, call run_crew with the path to the saved file
        response = run_crew(query=query.strip(), file_path=file_path)

        return {
            "status": "success",
            "query": query,
            "analysis": str(response), # Convert response to string for API output
            "file_processed": file.filename
        }

    except Exception as e:
        # Log the full exception for debugging in production
        print(f"Error during file processing or CrewAI run: {e}")
        import traceback
        traceback.print_exc() # Print full traceback to console/logs

        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")

    finally:
        # Clean up the uploaded file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up file: {file_path}")
            except OSError as e:
                print(f"Error removing file {file_path}: {e}") # Log if deletion fails

if __name__ == "__main__":
    import uvicorn
    # reload=True is good for development, disable in production for performance
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)