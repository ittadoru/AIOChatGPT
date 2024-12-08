# AIOChatGPT

## Project Description

**AIOChatGPT** is a Telegram bot designed to assist users with various AI-powered tasks. The bot provides an intuitive interface for communication, coding, and image analysis, adapting to each user's needs.

### Key Features:

1. **Chat Mode (ChatGPT):**  
   The bot answers questions, engages in conversations, and helps with everyday tasks.

2. **Coding Mode (Coder):**  
   Specialized for coding tasks: fixes, optimizes, or generates code. If the user enters an unformatted request, the bot reminds them about proper formatting for Telegram.

3. **Image Analysis Mode (Vision):**  
   The bot processes and analyzes image content.  
   _Note:_ Image-related tasks may take longer than text queries and are generally less stable.

### Highlights:

- The Vision model may generate responses slowly when running on a CPU or low-performance GPU.
- Responses are translated into English because **llama3.1** performs poorly with Russian.
- User data is stored in a binary file (future plans include migrating to Redis or MongoDB).

## Challenges and Solutions

1. **Mode Switching:**  
   Users often request tasks unrelated to the current mode. The bot solves this by suggesting switching to the appropriate mode.

2. **Optimized Responses:**  
   Answers are automatically condensed to provide only the most relevant information, saving users' time and system resources.

3. **International Usage:**  
   Users can change the response language using the `/set_language` command (default is Russian).

## Bot Commands

- **/start** — Start using the bot.
- **/set_mode** — Select a mode: ChatGPT, Coder, or Vision.
- **/reset_history** — Clear the conversation history.
- **/change_model** — Switch to another model.
- **/clear_all_user_data** — Clear all user data (admin-only).
- **/clear_all_images** — Clear all photos in the `/photos` folder (admin-only).
- **/set_language** — Choose the communication language.

## About the Author

#### Charming, charismatic, irresistible, enigmatic, sophisticated, stylish, passionate, captivating, confident.
