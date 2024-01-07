# AI-Driven LinkedIn Job Application Bot 🤖

## Overview

This project leverages AI, specifically GPT models, to automate job applications on LinkedIn. It intelligently applies to jobs with the "Easy Apply" option and auto-fills application forms behalf of you.

## Getting Started

Before diving into the project, you'll need to create two essential files with the provided template:

1. **Text File:** Contains your resume and other relevant details to fill LinkedIn's Easy Apply forms.
2. **JSON File:** Houses various configuration settings for the job application process.

Refer to the example files in this project for guidance on creating your own. As a Machine Learning Engineer, I have crafted both the JSON and Text files specifically for applying to Machine Learning roles, aligning closely with my preferences. Feel free to use these as templates to adapt for other roles.

### 🗂 JSON File Configuration

The JSON file is crucial for tailoring the application process to your preferences. Below is the explanation of each key:

- `username`: Your LinkedIn account email.
- `password`: Your LinkedIn account password.
- `roles1`: List of keywords for desired job titles. The bot will apply if the job title contains any of these words.
- `not_roles1`: List of keywords to avoid in job titles. The bot will not apply to jobs with these keywords in the title.
- `keywords`: List of skills or job roles for the LinkedIn job search.
- `locations`: List of preferred job locations.
- `remote`: Set to `true` or `false`. If true, the bot searches for remote jobs.
- `hybrid`: Set to `true` or `false`. If true, the bot searches for hybrid jobs. If both `remote` and `hybrid` are true, it searches for both types. If both are false, it considers all job types (onsite, remote, hybrid).
- `telegram_token_id`: Your Telegram bot token for receiving updates on job applications and filled forms.
- `telegram_chat_id`: Your Telegram chat ID for receiving updates.
- `token_cookie_chatgpt`: ChatGPT cookie token. To obtain, visit [ChatGPT](https://chat.openai.com), press F12 for developer tools, find the `__Secure-next-auth.session-token` cookie, and copy its value.
- `headless_mode_chatgpt`: Set to `true` or `false`. If true, runs ChatGPT UI browser in headless mode. Currently, set it to false due to a known bug.
- `model_name`: The GPT model name (e.g., "gpt-4", "gpt-3.5").
- `gemini_api_key`: API key for Google Gemini. Obtain it [here](https://makersuite.google.com/app/apikey).
- `chatgpt_timeout`: Time in seconds (default 120) to wait before retrying a request in case of an error with ChatGPT response extraction.
- `GPT_backend_selection`: Choose between "chatgpt" and "gemini". Use "chatgpt" for ChatGPT token or "gemini" for Gemini API key.

### 🚀 Quick Tips:


- The project uses the ChatGPT web UI for response extraction, offering a cost-effective solution.
- Choose GPT-4 if you are subscribed to ChatGPT Plus else choose GPT-3.5.
- Gemini might be a better option if ChatGPT is slow, though currently, GPT-3.5 and GPT-4 seems more accurate in answering questions in this task than Gemini. But if you find Gemini is performing well for you, please free to use it.
- This project uses Undetected-Chromedriver to keep the bot hidden and prevent it from being blocked.

## License

This project is licensed under the [Apache License](LICENSE).

### Important Warning ⚠️

LinkedIn may block your account if it detects automation tools being used without permission. This has happened to me several times. To mitigate this risk, the code includes sleep intervals and uses an undetected-chromedriver, aiming to reduce the chances of detection by LinkedIn. However, please be aware that LinkedIn might still detect and permanently block your account. **I am not responsible for any account suspensions or bans that may occur as a result of using this tool.**

Use this tool wisely and at your own risk. Happy job hunting! 🎯🤖

---
*Disclaimer: This project is not affiliated with LinkedIn or OpenAI. Use responsibly and adhere to LinkedIn's terms of service.*
