<a name="readme-top"></a>
<p align="center">
    <a href="https://www.2pods.net" style="margin: 0px 10px; text-decoration: none;">
        <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/heading_CB.gif">
    </a>
</p>

<p align="center">
    <a href="https://www.2pods.net" style="margin: 0px 10px; text-decoration: none;">
        <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/2pods.png" style = "width: 40%;">
    </a>
</p>

---

<div align="center">
  <div style="display: flex; justify-content: center;">
    <a href="https://open.spotify.com/show/1Q5FjHPnbtyz8shYBqqyXC" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/badges/badge_spotify.png" style="width: 200px; height: 49px;">
    </a>
    <a href="https://podcasts.apple.com/us/podcast/newsbytes/id1684407002" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/badges/badge_apple.svg" style="width: 200px; height: 49px;">
    </a>
    <a href="https://podcasts.google.com/feed/aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL25ldXRyYWxuZXdzLWF1ZGlvLWJ1Y2tldC9OZXdzQnl0ZV9SU1MueG1s" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/badges/badge_google.png" style="width: 200px; height: 49px;">
    </a>
    <a href="https://player.fm/series/newsbytes" style="margin: 0px 10px; text-decoration: none;">
      <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/badges/badge_playerfm.png" style="width: 200px; height: 49px;">
    </a>
  </div>
  <a href="https://www.producthunt.com/posts/2pods?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-2pods" target="_blank">
  <img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=392634&theme=dark" alt="2pods - AI&#0032;Generated&#0032;Automated&#0032;Podcasting | Product Hunt" style="width: 200px; height: 59px; margin-top: 10px;" width="200" height="59" />
  </a>
</div>


<br/>

<!-- ABOUT THE PROJECT -->
## About 🔰

CryptoBytes is an AI generated podcast that covers the latest crypto news in roughly 5 minutes. CryptoBytes is a vertical which pushes the boundaries of what is capable. This specific podcast incorporates an AI with a sense of humour to deliever a more natural sounding news podcast. As a part of [2pod's](https://www.2pods.net) Byte Podcasts, CryptoBytes is able to post a new podcast every 24 hours is with all its content, from the podcast audio to descriptions being AI generated. Keeping up with that theme, the podcast cover seen on spotify is also AI generated. See the image below for a detailed look at the tech stack used.

## Why Sponsor? 🫶🏼
If you enjoy the content of NewsBytes, or believe in the potential of AI backed podcasting consider sponsoring! It will greatly help in keeping this self funded project afloat. Sponsoring will help cover API & Storage costs - as well as allowing [2pods](https://www.2pods.net) to grow.  
  
<a href=https://github.com/sponsors/Zafirmk>
    <img src="https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#EA4AAA"/>
</a>
   

## Built With 🔧

### Version 1.0+ 📌
<p align="center">
    <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/stack_CB.png">
</p>

### Version 2.0+ 📌
<p align="center">
    <img src="https://github.com/Zafirmk/NewsBytes/blob/NewsBytes/Images/stackv2_CB.png">
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
See .env.sample file
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>


### SO-VITS-SVC Setup (v1.*) 🔩

Once the API keys are setup, you will need a model and config file corresponding to the voice you want to use for the podcast.

- Follow this [page](https://github.com/voicepaw/so-vits-svc-fork) to train your own voice model
- Or, download pre-trained models from this [page](https://huggingface.co/models?search=so-vits-svc-4.0)

Place the path to the download links into ``MODEL_URL`` and ``MODEL_CONFIG``
Example: 
```
MODEL_URL = https://huggingface.co/xgdhdh/so-vits-svc-4.0/resolve/main/Saber/G_30400.pth
MODEL_CONFIG = https://huggingface.co/xgdhdh/so-vits-svc-4.0/raw/main/Saber/config.json
```

Note: If you are using v2.*, this set up is not required. Only an API key for ElevenLabs is required.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- POTENTIAL IMPROVEMENTS -->
## Potential Improvements ⚙️

- [ ] Optimize [2pods](https://www.2pods.net) website for mobile
- [ ] Improve web scrapping model
    - Current version drops certain news articles if news can not be extracted via BoilerPy3

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

<a href="mailto:zafir@2pods.net">
    <img src="https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Gmail">
</a>

<a href="https://www.linkedin.com/in/zafirmk/">
    <img src="https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white" alt="Linkedin">
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>
