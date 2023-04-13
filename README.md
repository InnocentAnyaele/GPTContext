![GPTContext](https://user-images.githubusercontent.com/55434969/225579902-ffe9a506-3cc3-4bfa-aca3-e563bcfe87eb.png)


# GPTContext

The React front end for GPTContext app that allows user to upload context files and query chat GPT AI based on it.

## Technical Overview

The project leverages dataloaders from Llama Hub AI to create indices over the data that is being fed through the front-end. The files are stored in a directory in the server to be processed and deleted after 5 minutes. The Llama index library is used to process the data which is then passed into a GPTSimpleVectorIndex to create an index.

## Installation Backend

1. Get an OpenAI API key and store it in a file named `keys.py` at the root directory with the name `OPENAI_API_KEY`.
2. Create a random bearer token and store it in your keys file with the name 'BEARER TOKEN'. This key would be the same with the REACT_APP_BEARER_TOKEN passed with your request from the frontend.
2. Download the project from GitHub.
3. Open a terminal and navigate to the project directory.
4. Install the Python dependencies by running the following command:
``` pip install -r requirements.txt ```
5. Run the flask server with the following command ``` python app.py ```

## Installation Frontend

1. Download the project from GitHub.
2. Open in a terminal.
3. ```npm install``` to install all dependencies
4. ```npm start``` to start the server.
5. Create a .env file and create a environmental variable 'REACT_APP_BEARER_TOKEN'. This would be the same with the BEARER_TOKEN at the flask backend for authentication purposes

### The front-end uses a hosted PythonAnywhere server for its server requests. If you want to host it locally, follow the backend configurations above and get the locally hosted link and follow the steps below
1. In the frontend directory inside the components/body, open the body.tsx file.
2. There are two axios request that uses the 'https://1nnocent.pythonanywhere.com' for their prefix.
3. Replace this prefix with the locally hosted route eg. 'http://127.0.0.1:5000'
4. Restart the server.
5. Project should run locally now.

## Usage
- In the web application, drag your files into the blue zone, or select choose file and choose your files.
- Click submit.
- The files will be uploaded and processed.
- There should be a confirmation message prompting you to now start the conversation.
- The session would expire in 5 minutes and your files will be deleted from the server.
- The application will restart.
- You can always restart the session by clicking tthe refresh icon at the bottom left of the interface


## Contributing

I welcome contributions from anyone! To contribute to this project, follow these steps:

1. Fork the repository to your own GitHub account.
2. Clone the forked repository to your local machine.
3. Create a new branch for your changes with a descriptive name (e.g., `fix-bug-123`).
4. Make your changes to the codebase.
5. Commit your changes with a clear and descriptive commit message.
6. Push your changes to your forked repository.
7. Create a pull request (PR) from your forked repository to the original repository's `master` branch.
8. Describe your changes in the PR description and link to any relevant issues or pull requests.
9. Wait for feedback.

Thank you for your interest in contributing to this project!




