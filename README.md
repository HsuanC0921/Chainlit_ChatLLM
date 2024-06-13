# Chainlit ChatLLM

Chainlit ChatLLM is a simple chatbot application developed as a senior project. It leverages the Chainlit framework and integrates with a local LLM (Large Language Model) server to provide an interactive conversational experience.

## Live Demo

A live demo of the Chainlit ChatLLM is available at: [http://140.238.50.158:8501](http://140.238.50.158:8501)

Please note that the demo may not always be accessible due to server maintenance or other factors. We apologize for any inconvenience this may cause.

## Local Setup

To run the Chainlit ChatLLM locally, please follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Chainlit_ChatLLM.git
   ```

2. **Install the required packages:**
   ```bash
   cd Chainlit_ChatLLM
   pip install -r requirements.txt
   ```

3. **Start the local LLM server by executing the `start-llmserver.sh` script:**
   ```bash
   ./start-llmserver.sh
   ```
   This script will launch the llama.cpp.server, which simulates the OpenAI API.

4. **In a separate terminal, start the web UI by running the `start-webui.sh` script:**
   ```bash
   ./start-webui.sh
   ```
   This script will initiate the Chainlit web UI interface.

5. **Open a web browser and navigate to the provided URL to access the Chainlit ChatLLM.**

## Technologies Used

- **Chainlit**: A framework for building conversational AI applications.
- **llama.cpp.server**: A local server that emulates the OpenAI API.
- **Python**: The programming language used for development.
- **HTML/CSS**: For creating the web-based user interface.

## Contributing

We welcome contributions to the Chainlit ChatLLM project! If you encounter any issues or have ideas for enhancements, please feel free to open an issue or submit a pull request on the GitHub repository. We appreciate your feedback and support.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

We would like to express our gratitude to the following:

- The Chainlit team for providing the framework and documentation.
- The developers of llama.cpp.server for enabling local LLM serving.
- The open-source community for their valuable contributions and inspiration.

Thank you for your interest in the Chainlit ChatLLM project. We hope you find it useful and enjoy interacting with the chatbot!
