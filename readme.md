# RankingPal

RankingPal is a web app that allows you to keep a [TrueSkill](http://research.microsoft.com/en-us/projects/trueskill/default.aspx) ranking for a 4 player cards game (such as Hearts). 
The app uses a database and has these features:
- Player Ranking Table
- Game scores log page
- Insert score for games
- Insert new player names
- Admin page:
-- Reset scores/games
-- Deleted specific game scores
-- Regenerate rankings


The app is live here: [http://rankingpal.appspot.com/](http://rankingpal.appspot.com/)


## Tech stack
### Server side:
 - Python 2.7 app hosted on [Google AppEngine Standard Environment](https://cloud.google.com/appengine/docs/standard/python/runtime)
 - Jinja 2 templates
 - Database: [Google "NoSQL" Datastore](https://cloud.google.com/datastore/)
 - OAuth authentication integration for google accounts 


### Front-end:
 - HTML, CSS
 - Javascript
 - jQuery
 - [script.aculo.us](http://madrobby.github.io/scriptaculous/autocompleter-local/) (for input autocomplete)

## Acknowledgments
 - TrueSkill python library by Doug Zongker (Apache License 2.0)
   [https://github.com/dougz/trueskill](https://github.com/dougz/trueskill)
