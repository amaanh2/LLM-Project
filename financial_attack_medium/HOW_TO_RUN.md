# Financial Attack - Medium
## By Travis Durrant
This file describes how to run the CTF challenge, and the goal.

### Motivation
Many apps that integrate LLMs use external APIs rather than running them locally. These APIs often place steep costs on calls to the models. Even when run locally, LLMs often create a large hidden cost in computing power, and raw power consumption. This challenge focuses on exploiting a vulnerability in a web app that makes calls to an external API. (It does need to run locally for this challenge, because trying to actually use those APIs in a deliberate CTF violates their TOS. I hope you don't like having spare RAM.) This particular web-app is very evil and has bad business practices, or maybe you're the evil one in the scenario, so you are going to exploit this inherent vulnerability to force them to take down their application. It should be impossible to miss the success condition, as it renders a unique HTML page.

### How to Run
Prerequisite:
Present working directory is {somepath}/financial_attack_medium

1st commmand:
docker build -t financial-attack-ctf .

*This will generate the image needed to spawn a container. The name is non-essential, but make sure it matches if you change it.*

2nd command:
docker run -d -p 5000:5000 financial-attack-ctf

*This will spawn a container from the previously generated image. It loads the model on startup, so it will take a moment. You can use the command docker logs {container} if you suspect it is not working for some reason, and when you see the text 'device set to use cpu' that means it is running.*

The web server will be available at localhost:5000