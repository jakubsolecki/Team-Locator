[![](https://img.shields.io/badge/python-3.7-blue)](https://www.anaconda.com/products/individual)
[![](https://img.shields.io/badge/kivy-1.11.1-lightgrey)](https://kivy.org/#home)
[![](https://img.shields.io/badge/platform-android-green)](https://developer.android.com/)

# Team-Locator

Team-Locator is a mobile app developed using Python Kivy corss-platform framework. The app helps to improve outdoor games coordination.

# Usage

Run ```python server.py``` ona a computer connected to the network, that has ```port 5050``` opened. Read more in the [Server](#server) section.

## Mobile app

**IP address** - IP address of the server.

**Nickname** - username that will be displayed on the map.

**Team / Host code** - token for team obtained from Host or a special Host token for game supervisor.

## Users

There are 2 types of users:
* Host
* Players

### Host
***It is advised for the Host to have access to the server (eg. using Thermux ssh)***. <br/>
Host is the supervisor of the game. Host manages the game, creates required number of teams (1-10), starts/ends game and provides tokens to teams. This person is also the only one able to see all players on the map while having the ability to share own location with everyone or remain transparent. 

#### Quick guide
1.  To become host, one must provide special token obtained form server's console after startup. The default token is ```/00/``` and is hardcoded in the ```server.py``` (You are free to change it any time). After filling all inputs the Host can use ```Host Game``` button. <br/><br/>
2.  Now you can choose whether You want to be visible (```Host widoczny```) and adjust number of teams. Colors of teams' names correspond to their pins on map. It is worth noting that the Host is ***always black***. <br/><br/>
3.  Now click ```connect```. <br/><br/>
4.  After landing on the map go to ```Codes``` (top left) and provide one token for each team. Each game generates new tokens. <br/><br/>
5.  To finish the game go to the ```Stop``` (top right). You will be asked to confirm. After ```Yes```, the Host **and all players** will be redirected to the main screen.

### Player
Players can only see their teammates on map. After receiving token from Host just click ```Connect Game```.

## Server
Server is the core and allows mobile devices with Team-Locator to exchange data about location. Server (```server.py```) must be running on a computer with an internet connection and ```port 5050``` opened for global traffic. (*Therefore, we recommend running it on some kind of VM server - we used DigitalOcean's droplet with Linux*). Script can be run like any Python script, because it relies only on the standard library. _Remeber, that you can always access these kind of servers from your phone, using ssh (Thermux is awesome for that!)_ <br/>

***Run server:*** ```python server.py``` (be sure to use python 3.x).<br/>
***Stop server:*** ```Ctrl + C``` in server's console. 

Server can handle multpile games but not at the same time. You can run it once and forget about it. Everything else can be configured from app's level.

## Demo

TODO :)

# Contributors:
<table>
  <tr>
    <td align="center"><a href="https://github.com/jakubsolecki"><img src="https://avatars2.githubusercontent.com/u/57220835?s=460&v=4" width="100px;" alt=""/><br /><sub><b>Jakub Solecki</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/skupien"><img src="https://avatars3.githubusercontent.com/u/32012668?s=460&v=4" width="100px;" alt=""/><br /><sub><b>Patryk Skupień</b></sub></a><br />
    </td>
  </tr>
</table>
