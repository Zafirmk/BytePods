<a name="readme-top"></a>
<p align="center">
    <img src="https://github.com/Zafirmk/NeutralNews-Podcast/blob/main/Images/heading.gif">
</p>

---

<div align="center">
  <div style="display: flex; justify-content: center;">
    <a href="https://open.spotify.com/show/1Q5FjHPnbtyz8shYBqqyXC" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NeutralNews-Podcast/blob/main/Images/badges/badge_spotify.png" style="width: 200px; height: 49px;">
    </a>
    <a href="https://podcasts.apple.com/us/podcast/newsbytes/id1684407002" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NeutralNews-Podcast/blob/main/Images/badges/badge_apple.svg" style="width: 200px; height: 49px;">
    </a>
    <a href="#" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NeutralNews-Podcast/blob/main/Images/badges/badge_google.png" style="width: 200px; height: 49px;">
    </a>
    <a href="https://player.fm/series/newsbytes" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NeutralNews-Podcast/blob/main/Images/badges/badge_playerfm.png" style="width: 200px; height: 49px;">
    </a>
  </div>
</div>

<br/>

<!-- ABOUT THE PROJECT -->
## About 🔰

NewsBytes is an AI generated spotify podcast that covers global headlines in roughly 5 minutes. Sourcing through [ground.news](https://www.ground.news), NewsBytes is able report from neutral sources only. Every 24 hours a new podcast is posted with all its content, from the podcast audio to descriptions being AI generated. Keeping up with that theme, the podcast cover seen on spotify is also AI generated. See the image below for a detailed look at the tech stack used.

### Built With 🔧

<p align="center">
    <img src="https://github.com/Zafirmk/NeutralNews-Podcast/blob/main/Images/stack.png">
</p>

### Labels 🏷
[![Pylint](https://github.com/Zafirmk/NewsBytes/actions/workflows/pylint.yml/badge.svg)](https://github.com/Zafirmk/NewsBytes/actions/workflows/pylint.yml)
<a href="https://github.com/Zafirmk/NewsBytes/releases/tag/v1.0">
    <img alt="GitHub release (latest by date)" src="https://img.shields.io/github/v/release/Zafirmk/NewsBytes?color=green&label=Latest%20Release">
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started 🔌

### Requirements 📦

Before starting with the project, you need to have a few requirements installed:

- Python 3.10
- Pip

You can install the required Python packages by running the following command:

```
pip install -r requirements.txt
```

### Setting ENV Variables 🔑

The project requires API keys for Google Cloud Platform & OpenAI's ChatGPT to access the necessary services.
You can set up your API keys by following these steps:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the necessary APIs for your project:
   - Cloud Text-to-Speech API
   - Cloud Storage API
4. Download the JSON key for your service account.

```
OPENAI_API_KEY = OpenAI API key
OPENAI_PROMPT = OpenAI prompt to summarize news articles
OPENAI_DESCRIPTION_PROMPT = OpenAI prompt to create episode description
GOOGLE_APPLICATION_CREDENTIALS = Path to GCP credentials json
BUCKET_NAME = GCP bucket name
MODEL_URL = Download link to so-vits-svc model (.pth file)
MODEL_CONFIG = Download link to so-vits-svc model config (.json file)
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### SO-VITS-SVC Setup 🔩

Once the API keys are setup, you will need a model and config file corresponding to the voice you want to use for the podcast.

- Follow this [page](https://github.com/voicepaw/so-vits-svc-fork) to train your own voice model
- Or, download pre-trained models from this [page](https://huggingface.co/models?search=so-vits-svc-4.0)

Place both the .pth model file and config.json in the root directory.
Example: ``./G_58000.pth`` and ``./config.json``


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- POTENTIAL IMPROVEMENTS -->
## Potential Improvements ⚙️

- [ ] Tweak TTS naturalization
    - Current version may encounter voice cracks
    - See NewsByte: 003
- [ ] Include news from subtopics (Finance, Sports etc.)
- [ ] Improve web scrapping model
    - Current version drops certain news articles if news can not be extracted via BoilerPy3
- [ ] Ensure two consecutive podcasts do not repeat news
    - See NewsByte: 005 and NewsByte: 006

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing 📄

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License 🔒

Distributed under the Apache-2.0 license. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact 📞

<a href="mailto:zafirmk0@gmail.com">
    <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
</a>

<a href="https://www.linkedin.com/in/zafirmk/">
    <img src="https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Linkedin">
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
