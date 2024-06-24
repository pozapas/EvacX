
# EvacX Bot

EvacX bot is an automated solution designed to enhance the visibility of recent research publications in the field of crowd evacuation. The app automates the process of discovering, summarizing, and disseminating new research findings through Twitter, ensuring timely and consistent updates for the academic and professional communities.

## Features

- Automatically discovers new research publications from multiple journals.
- Summarizes the research findings.
- Disseminates the summaries through Twitter.
- Ensures timely and consistent updates.

## Setup and Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/pozapas/EvacX.git
   cd EvacX-bot
   ```

2. **Install Required Packages**

   Ensure you have `pip` installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**

   You need to set up your API keys for Twitter and Stable Diffusion. Update the following variables in `EvacX.py` with your credentials:

   ```python
   api_key = 'YOUR_TWITTER_API_KEY'
   api_key_secret = 'YOUR_TWITTER_API_KEY_SECRET'
   access_token = 'YOUR_TWITTER_ACCESS_TOKEN'
   access_token_secret = 'YOUR_TWITTER_ACCESS_TOKEN_SECRET'
   client_id = 'YOUR_TWITTER_CLIENT_ID'
   client_secret = 'YOUR_TWITTER_CLIENT_SECRET'
   bearer_token = 'YOUR_TWITTER_BEARER_TOKEN'
   STABILITY_KEY = 'YOUR_STABLE_DIFFUSION_API_KEY'
   ```

4. **Run the Bot**

   To start the bot, simply run:

   ```bash
   python EvacX.py
   ```

## Journals Monitored

The bot monitors new publications from the following journals:

- Safety Science
- Fire Technology
- Fire Safety Journal
- Automation in Construction
- Advanced Engineering Informatics
- International Journal of Disaster Risk Reduction
- Physica A
- Transportation Research Part A, B, C, D, and F
- Environmental Hazards
- Transportation Planning and Technology

## Contributing

We welcome contributions to enhance the bot's functionality or to include more journals. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries or suggestions, please contact amir.rafe@usu.edu.

---

Check out the EvacX Twitter account [here](https://x.com/EvacuationModel).
