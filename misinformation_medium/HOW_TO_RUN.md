# How to Run This Web App

This section outlines the steps to set up and run the vulnerable web application locally using Docker.

## Prerequisites:

**Docker:** Ensure that Docker is installed and running on your system. You can download and install it from the official Docker website: [https://www.docker.com/get-started/](https://www.docker.com/get-started/)

## Steps:

1.  **Clone the Repository:** Open your command prompt or terminal and run the following command to clone the entire repository containing the vulnerable web application:

    ```bash
    git clone [https://github.com/CSCI3540U/ctf-major-project-team-sudo](https://github.com/CSCI3540U/ctf-major-project-team-sudo)
    ```

2.  **Navigate to the Directory:** Change your current directory in the command prompt or terminal to the `misinformation_medium` directory within the cloned repository:

    ```bash
    cd ctf-major-project-team-sudo/misinformation_medium
    ```

3.  **Build the Docker Image:** Use the following command to build a Docker image for the web application. This command will read the `Dockerfile` in the current directory and create an image named `llm_misinformation`:

    ```bash
    docker build -t llm_misinformation .
    ```

4.  **Run the Docker Container:** Once the image is built successfully, run the following command to start the web application within a Docker container. This command maps port 5000 on your local machine to port 5000 inside the container, where the application is running:

    ```bash
    docker run -p 5000:5000 llm_misinformation
    ```

5.  **Access the Web Application:** Open your web browser (e.g., Chrome, Firefox, Safari) and navigate to the following address:

    ```
    http://localhost:5000
    ```
