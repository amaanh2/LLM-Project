LLM File Upload CTF Challenge

DESCRIPTION:
------------
This is a Capture-the-Flag style Flask application that allows users to upload .txt files.
If a special "trigger" phrase is detected in the uploaded file, a secret flag is revealed.

------------------------------------------------------------
HOW TO BUILD & RUN THIS PROJECT USING DOCKER
------------------------------------------------------------

NOTICE: PLEASE DOWNLOAD MY PROJECT FOLDER SEPARATE FROM THE REPOSITORY OR THE CHALLENGE WILL GET MESSED UP.


1. Open your terminal and navigate to the project folder:

    cd llm_file_upload_indirect_prompt_inject_noor_medium

2. Build the Docker image:

    sudo docker build -t llm-ctf .  

3. Run the Docker container on port 9000:

    sudo docker run -p 9000:9000 llm-ctf  

5. Open your browser and visit:

   localhost:9000/

------------------------------------------------------------
USAGE:
------------------------------------------------------------
As this is a web application, search through the web app and its pages to find any hints as to 
how to solve this CTF challenge. 

