import os
import sys
import re
import time
import asyncio
import subprocess
import traceback
import xml.etree.ElementTree as ET
from openai import AsyncOpenAI

# OpenAI API configuration
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4")

client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE)

system_message = """
You are a collective of super genius talented expert developers who can build any application flawlessly. Your task is to create sophisticated business applications and software solutions using Python, following specific guidelines and responding to user queries.

As a team of unparalleled experts, you possess an extraordinary ability to conceptualize, design, and implement complex software systems with ease. Your vast knowledge spans all aspects of software development, from intricate algorithms to cutting-edge architectural patterns.

Your collective intellect allows you to foresee and preemptively solve any potential issues, resulting in code that is not only functional but also elegant, efficient, and highly optimized. You have an innate understanding of user experience and can create intuitive interfaces that enhance productivity and user satisfaction.

In this role, you will:
1. Analyze business requirements with lightning speed and pinpoint accuracy.
2. Design software architectures that are both robust and flexible, anticipating future scalability needs.
3. Write flawless Python code that leverages the full potential of modern libraries and frameworks.
4. Implement advanced features that go beyond the client's expectations, showcasing your exceptional problem-solving skills.
5. Optimize performance to ensure smooth operation even with large datasets or high user loads.
6. Provide clear, concise, and insightful documentation that explains your genius-level solutions.

Remember, as super genius developers, you're not just meeting requirements – you're redefining what's possible in business software development. Your code should reflect this extraordinary level of expertise and innovation.

Follow these instructions to formulate your response:
1. Read the query carefully and analyze any provided information.
2. Tap into your collective genius to devise the most elegant and efficient solution.
3. Write your response in the same language as the query.
4. Provide your extraordinary solution directly, without explaining your process or citing sources.
5. Use appropriate markdown formatting to enhance readability, including code blocks with syntax highlighting for Python code.

Your goal is to create business applications that not only meet but far exceed expectations, showcasing the pinnacle of what's achievable in Python software development.
"""

PRINT_RESPONSE = True

print("Welcome to Agent Application Dev!")
print("This tool will help you create a Python business application using AI assistance.")
print("Please follow the prompts carefully and enjoy the application development process!")
print()

user_consent = input("WARNING: THIS SCRIPT WILL AUTOMATICALLY EXECUTE CODE ON YOUR MACHINE. THIS CAN BE POTENTIALLY DANGEROUS. IF YOU UNDERSTAND AND ACCEPT THIS RISK, PLEASE TYPE 'YES' TO CONTINUE: ").strip().upper()
if user_consent != "YES":
    print("Script execution aborted.")
    sys.exit(0)

print("User consent received. Proceeding with Agent Application Dev.")

try:
    if os.path.exists("app"):
        import shutil
        shutil.rmtree("app")
except Exception as e:
    print(f"Please close any terminal which has app folder open and run the application again. Error: {e}")

def add_separator_between_consecutive_user_messages(messages):
    for i in range(len(messages) - 1):
        if messages[i]["role"] == "user" and messages[i+1]["role"] == "user":
            messages.insert(i+1, {"role": "assistant", "content": "..."})
    return messages

async def plan_project(user_input, iterations):
    system_message_1 = f"""
    You are a logical, critical software design expert. Your role is to discuss and plan with a critical and rigorous eye, a Python business application project based on user input. One of the main goals is to review the logic of the code to ensure a functional and efficient application experience for the user.
    Focus on application architecture, structure, and overall design and function and method inputs (proper inputs and number of inputs) and returns of functions and methods. Do not suggest external media files or images. Make sure no code files need any external files. Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur. No need to discuss timelines or git commands. Main purpose is to review and evaluate the project structure so that when the final files and their descriptions are prepared the code will function without any errors.
    Remember that the application should start with a main module in the main.py file.
    Here is the user input: {user_input}
    """

    system_message_2 = f"""
    You are a logical, critical Python architecture expert. Your role is to discuss and plan with a critical and rigorous eye the file structure for a Python business application project. One of the main goals is to review the logic of the code to ensure a functional and efficient application experience for the user.
    Focus on code organization, modularity, and best practices and function and method inputs (proper inputs and number of inputs) and returns of functions and methods. Do not suggest external media files or images. Make sure no code files need any external files. Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur. No need to discuss timelines or git commands. Main purpose is to review and evaluate the project structure so that when the final files and their descriptions are prepared the code will function without any errors.
    Remember that the application should start with a main module in the main.py file.
    Here is the user input: {user_input}
    """

    messages_1 = [{"role": "user", "content": f"Please plan a Python business application project based on the following user input: {user_input}. Remember that the application should start with a main module in the main.py file."}]
    messages_2 = []

    for i in range(iterations):
        print(f"Iteration {i+1} of {iterations} planning iterations")
        is_final = i == iterations - 1

        if is_final:
            messages_1.append({"role": "user", "content": "This is the final iteration. Please provide your final application structure along with file structure you think is best for the application. Don't return any directories but just the file names and descriptions. Make sure to mention what imports are necessary for each file. Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur. Ensure function and method inputs are accurate as well as their returns. Remember that the application should start with a main module in the main.py file (main shouldn't take any arguments)."})

        messages_1 = add_separator_between_consecutive_user_messages(messages_1)
        response_1 = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message_1},
                *messages_1
            ],
            max_tokens=4000000
        )

        if PRINT_RESPONSE:
            print(response_1.choices[0].message.content)

        messages_1.append({"role": "assistant", "content": response_1.choices[0].message.content})
        messages_2.append({"role": "user", "content": response_1.choices[0].message.content})

        if is_final:
            messages_2.append({"role": "user", "content": "This is the final iteration. Please review the application design carefully and provide your final response in the following XML format:\n<application_plan>\n  <overview>Overall application description</overview>\n  <architecture>Key application architecture</architecture>\n  <files>\n    <file>\n      <name>filename.py</name>\n      <description>File purpose and contents</description>\n    </file>\n    <!-- Repeat <file> element for each file -->\n  </files>\n</application_plan>. Please don't return any additional directories but just the file names and descriptions along with simple description of functions and methods along with their inputs and returns. Please return descriptions for all files. We will save all files in the same folder. Make sure to mention what imports are necessary for each file. Critical objective is to keep the project structure simple while making sure no circular imports or broken imports occur as well as the clear and accurate definition of function and method inputs. Remember that the application should start with a main module in the main.py file (main shouldn't take any arguments)."})

        messages_2 = add_separator_between_consecutive_user_messages(messages_2)
        response_2 = await client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message_2},
                *messages_2
            ],
            max_tokens=4000000
        )

        if PRINT_RESPONSE:
            print(response_2.choices[0].message.content)

        messages_2.append({"role": "assistant", "content": response_2.choices[0].message.content})
        messages_1.append({"role": "user", "content": response_2.choices[0].message.content})

    xml_content = re.search(r'<application_plan>.*?</application_plan>', response_2.choices[0].message.content, re.DOTALL)
    if xml_content:
        return xml_content.group(0)
    else:
        raise ValueError("No valid XML content found in the response")

async def agent_write_file(file_name, file_description, application_plan):
    print(f"Creating file '{file_name}'...")
    os.makedirs("app", exist_ok=True)

    system_message = """
    You are a Python application development expert. Your task is to write an error-free Python file for a business application based on the overall project structure. Always return the full contents of the file. One of the main goals is to review the logic of the code to ensure a functional and efficient application experience for the user.
    Do not include any external media files or images in your code.
    Write clean, well-commented code that follows best practices.
    The application should start with a main module in the main.py file (main shouldn't take any arguments).
    Return the code for the file in the following format:
    <code>
    file_code
    </code>
    """

    prompt = f"""Create a Python file named '{file_name}' with the following description: {file_description}

    Here's the overall application plan which you should follow while writing the file:

    {application_plan}

    Remember, the application should start with a main module in the main.py file (main shouldn't take any arguments). Always return the full contents of the file.
    """

    response = await client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000000
    )

    code = response.choices[0].message.content
    code = code.split("<code>")[1].split("</code>")[0]
    with open(f"app/{file_name}", "w", encoding="utf-8") as f:
        f.write(code)
    print(f"File '{file_name}' has been created.")

def parse_file_structure(xml_string):
    root = ET.fromstring(xml_string)
    files = []
    for file_elem in root.findall('.//file'):
        name = file_elem.find('name').text
        description = file_elem.find('description').text
        files.append((name, description))
    return files

async def run_application():
    print("Running the application...")
    full_output = ""
    full_error = ""
    try:
        process = subprocess.Popen(
            [sys.executable, "-c", "import sys; sys.path.insert(0, 'app'); import main; main.main()"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print("Application is running. Please interact with the application. Close the window to stop.")
        while True:
            try:
                output = process.stdout.readline()
                error = process.stderr.readline()
                if output:
                    full_output += output
                    print(output.strip())
                if error:
                    full_error += error
                    print(f"Runtime error: {error.strip()}")
                if process.poll() is not None:
                    break
                await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                print("\nApplication stopped by user.")
                process.terminate()
                break

        stdout, stderr = process.communicate()
        full_output += stdout
        full_error += stderr

        if process.returncode != 0:
            full_error += f"\nProcess exited with return code {process.returncode}"
    except Exception as e:
        full_error += f"\nError running application: {str(e)}\n{traceback.format_exc()}"

    error_summary = ""
    if full_error:
        error_summary += f"Runtime errors:\n{full_error}\n"
    if "error" in full_output.lower() or "exception" in full_output.lower():
        error_summary += f"Possible errors in output:\n{full_output}\n"

    if error_summary:
        print(error_summary)
        return error_summary
    else:
        print("Application completed successfully")
        return None

async def fix_application_files(error_message):
    print("Attempting to fix the error...")
    error_filenames = re.findall(r'.*?([^/\\]+\.py)"', error_message)
    error_filenames = list(set(error_filenames))
    error_filenames = [f for f in error_filenames if f != 'agent_application_maker.py']

    file_contents = {}
    for filename in os.listdir('app'):
        if filename.endswith('.py'):
            with open(os.path.join('app', filename), 'r') as f:
                file_contents[filename] = f.read()

    if error_filenames:
        print(f"Error occurred in files: {', '.join(error_filenames)}")
    else:
        print("Could not determine specific files causing the error")
    print(f"Sending all files for error correction: {', '.join(file_contents.keys())}")

    system_message = """
    You are a Python application development expert. Your task is to fix errors in Python project files.
    Analyze the error message and the contents of the application files, then provide the corrected versions of the files.
    Remember that the application should start with a main module in the main.py file (main shouldn't take any arguments).
    Carefully reason about the error in a step by step manner ahead of providing the corrected code. No external files are allowed within the application. One of the main goals is to review the logic of the code to ensure a functional and efficient application experience for the user.
    <reasoning>
    reasoning about the error
    </reasoning>
    Return the corrected file contents in the following format only for the files that requires correction:
    <file name="filename.py">
    corrected_file_contents
    </file>
    """

    prompt = f"""An error occurred while running the Python project. Here's the error message:
    {error_message}
    Here are the contents of the files involved in the error:
    {file_contents}
    Please analyze the error and provide corrected versions of the files to resolve the error. Return the full content of the files. Remember that the application should start with a main module in the main.py file (main shouldn't take any arguments)."""

    response = await client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400000
    )

    if PRINT_RESPONSE:
        print(response.choices[0].message.content)

    corrected_files = re.fin

#Citations:
#[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/8114547/956a0718-1e6f-4313-a0c7-b05c39a49e77/paste.txt
