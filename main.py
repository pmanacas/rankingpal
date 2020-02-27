import cgi
import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import normal
import urllib
import types
import json
import logging
from google.appengine.api import memcache
from google.appengine.datastore import entity_pb
import trueskill
import trueskill_config
import operator

# ==============================================================
# DB MODELS:
# ==============================================================
class Player(db.Model):
    name = db.StringProperty()
    joindate = db.DateTimeProperty(auto_now_add=True)
    games_played = db.IntegerProperty(int, default = 0)
    mu = db.FloatProperty(default = trueskill_config.default_mu)
    previous_mu = db.FloatProperty(default = trueskill_config.default_mu)
    sigma = db.FloatProperty(default = trueskill_config.default_sigma)
    previous_sigma = db.FloatProperty(default = trueskill_config.default_sigma)
    current_skill = db.FloatProperty(default = 0.0)
    previous_skill = db.FloatProperty(default = 0.0)
    submiter = db.UserProperty()
    current_rank = db.IntegerProperty(int, default = 0)
    previous_rank = db.IntegerProperty(int, default = 0)
    
class Game(db.Model):
    dateplayed = db.DateTimeProperty(auto_now_add=True)
    submiter = db.UserProperty()
    player_keys = db.ListProperty(db.Key)
    player_names = db.StringListProperty()
    scores = db.ListProperty(int)
    
# ==============================================================
# HELPER FUNCTIONS:   
# ==============================================================
def loginmenu(u):
    if users.get_current_user():
        url = users.create_logout_url('/')
        url_linktext = 'Log out'
        user = users.get_current_user()
        email = user.email()
    
    else:
        url = users.create_login_url(u)
        url_linktext = 'Log in'
        email = ''
    return url, url_linktext, email

    
def unicode_urlencode(value):
    if type(value) is types.UnicodeType:
        return urllib.quote(value.encode("utf-8"))
    else:
        return urllib.quote(value)    

def serialize_entities(models):
    if models is None:
        return None
    elif isinstance(models, db.Model):
        # Just one instance
        return db.model_to_protobuf(models).Encode()
    else:
        # A list
        return [db.model_to_protobuf(x).Encode() for x in models]

def deserialize_entities(data):
    if data is None:
        return None
    elif isinstance(data, str):
        # Just one instance
        return db.model_from_protobuf(entity_pb.EntityProto(data))
    else:
        return [db.model_from_protobuf(entity_pb.EntityProto(x)) for x in data]

# ==============================================================
# MEMCACHE QUERIES:
# ==============================================================
def from_cache_else_query(cachekey):
    
    entities = deserialize_entities(memcache.get(cachekey))
    
    if cachekey == 'allplayers':
        if not entities:
            logging.debug('allplayers not in cache')
            entities = Player.all().order('-current_skill').fetch(1000)
            memcache.set(cachekey, serialize_entities(entities))
    
    elif cachekey == 'allplayers_byname':
        if not entities:
            logging.debug('allplayers_byname not in cache')
            entities = Player.all().order('name').fetch(1000)
            memcache.set(cachekey, serialize_entities(entities))

    elif cachekey == 'allgames':
        if not entities:
            logging.debug('allgames not in cache')
            entities = Game.all().order('-dateplayed').fetch(1000)
            memcache.set(cachekey, serialize_entities(entities))
    
    return entities
    
    
# ==============================================================
# REQUEST HANDLERS:
# ==============================================================
class MainPage(webapp.RequestHandler):
  
    def get(self):
        menu = loginmenu(self.request.uri)
        players = from_cache_else_query('allplayers')
        lastgame_players = self.request.get_all('p')    
        
        for p in players:
            p.name = p.name.encode("utf-8")
            p.rankdelta = p.previous_rank - p.current_rank
            if p.rankdelta > 0:
                p.rankdeltaispositive = True
            p.skilldelta = p.current_skill - p.previous_skill
            
            p.mudelta = p.mu - p.previous_mu
            if p.mudelta > 0:
                p.mudeltaispositive = True
            
            p.sigmadelta = p.sigma - p.previous_sigma
            if p.sigmadelta > 0:
                p.sigmadeltaispositive = True
            
            if p.skilldelta > 0:
                p.skilldeltaispositive = True
            if str(p.key()) in lastgame_players:
                    p.inlast = True

        template_values = {
          'page_title' : 'Ranking -  liga de King',
          'page_header' : 'Ranking -  liga de King',
          'players' : players,
          'url' : menu[0],
          'url_linktext' : menu[1],
          'user' : menu[2],
          'admin' : users.is_current_user_admin(),
          }
        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))


class FAQPage(webapp.RequestHandler):
  
    def get(self):
        menu = loginmenu(self.request.uri)
        
        template_values = {
          'page_title' : 'Ranking -  liga de King',
          'page_header' : 'Ranking -  liga de King',
          'url' : menu[0],
          'url_linktext' : menu[1],
          'user' : menu[2],
          'admin' : users.is_current_user_admin(),
          }
        path = os.path.join(os.path.dirname(__file__), 'templates/faq.html')
        self.response.out.write(template.render(path, template_values))

        
class GamesPage(webapp.RequestHandler):
  
    def get(self):
        menu = loginmenu(self.request.uri)
        games = from_cache_else_query('allgames')

        template_values = {
          'page_title' : 'Ranking -  liga de King',
          'page_header' : 'Ranking -  liga de King',
          'games' : games,
          'url' : menu[0],
          'url_linktext' : menu[1],
          'user' : menu[2],
          'admin' : users.is_current_user_admin(),
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/games.html')
        self.response.out.write(template.render(path, template_values))    


class GamesRSS(webapp.RequestHandler):
  
    def get(self):
        games = from_cache_else_query('allgames')
        limit = self.request.get('limit')
        if not limit:
            n = 10
        else:
            n = int(limit)
        recentgames = games[0:n]
        template_values = {
          'games' : recentgames,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/games-rss.html')
        self.response.headers["Content-Type"] = "application/xml"
        self.response.out.write(template.render(path, template_values))

        
class GameFormPage(webapp.RequestHandler):
    @login_required
    def get(self):
        menu = loginmenu(self.request.uri)
        
        user = users.get_current_user()
        url = users.create_logout_url('/')
        url_linktext = 'Logout / Cancel'
                    
        template_values = {
          'page_title' : 'Inserir Pontos',
          'page_header' : 'Inserir Pontos',
          'playeradded' : self.request.get('playeradded'),
          'url' : menu[0],
          'url_linktext' : menu[1],
          'user' : menu[2],
          'admin' : users.is_current_user_admin(),
          }

        path = os.path.join(os.path.dirname(__file__), 'templates/gameform.html')
        self.response.out.write(template.render(path, template_values))
  

class PutGame(webapp.RequestHandler):
    def post(self):

        game = Game()
        game.submiter = users.get_current_user()
        
        temp = [
                (int(self.request.get('entry.5.single')),self.request.get('entry.1.single'),db.Key(encoded = self.request.get('p1-key'))),
                (int(self.request.get('entry.6.single')),self.request.get('entry.2.single'),db.Key(encoded = self.request.get('p2-key'))),
                (int(self.request.get('entry.7.single')),self.request.get('entry.3.single'),db.Key(encoded = self.request.get('p3-key'))),
                (int(self.request.get('entry.8.single')),self.request.get('entry.4.single'),db.Key(encoded = self.request.get('p4-key'))),
        ]
        temp.sort()
        temp.reverse()
        
        game.player_names = [
                             temp[0][1],
                             temp[1][1],
                             temp[2][1],
                             temp[3][1],]
        
        game.player_keys = [ temp[0][2],
                             temp[1][2],
                             temp[2][2],
                             temp[3][2],]
        
        game.scores =       [temp[0][0],
                             temp[1][0],
                             temp[2][0],
                             temp[3][0],]
        
        players = db.get(game.player_keys)
        
        trueskill.SetParameters(
                                trueskill_config.beta,
                                trueskill_config.epsilon,
                                trueskill_config.draw_probability, 
                                trueskill_config.gamma
                                )
        
        for p, s in zip(players, game.scores):
            p.games_played = p.games_played + 1
            p.skill = (p.mu, p.sigma)
            p.rank = s*-1
        trueskill.AdjustPlayers(players)
        
        for p in players:
            p.previous_mu = p.mu
            p.mu = p.skill[0]
            p.previous_sigma = p.sigma
            p.sigma = p.skill[1]
            p.previous_skill = p.current_skill
            p.current_skill = p.mu - trueskill_config.k * p.sigma
        db.put(players)
        game.put()
        
        all_players = Player.all().order('-current_skill').fetch(1000)
        for i, p in enumerate(all_players):
            if p.previous_rank == 0:
                p.previous_rank = i + 1
            else:
                p.previous_rank = p.current_rank
            p.current_rank = i + 1
        db.put(all_players)
        memcache.delete_multi(['allgames','allplayers','allplayers_byname'])
        self.redirect('/?&p=' + str(game.player_keys[0]) + '&p=' + str(game.player_keys[1]) + '&p='+str(game.player_keys[2]) + '&p='+str(game.player_keys[3]))

        
class PlayerFormPage(webapp.RequestHandler):
    @login_required
    def get(self):
        menu = loginmenu(self.request.uri)
        
        user = users.get_current_user()
        url = users.create_logout_url('/')
        url_linktext = 'Logout / Cancel'
                    
        template_values = {
          'page_title' : 'Novo Jogador',
          'page_header' : 'Novo Jogador',
          'url' : menu[0],
          'url_linktext' : menu[1],
          'user' : menu[2],
          'error' : self.request.get('error'),
          'admin' : users.is_current_user_admin(),
          }

        path = os.path.join(os.path.dirname(__file__), 'templates/playerform.html')
        self.response.out.write(template.render(path, template_values))

        
class PutPlayer(webapp.RequestHandler):
    def post(self):

        player = Player()
        player.name = self.request.get('playername')
        if len(player.name) < 2:
            self.redirect('/playerform?error=O nome ' + unicode_urlencode(player.name) + ' e demasiado curto.')
        else:
            player.submiter = users.get_current_user()
            user = Player.all().filter('name =', player.name).get()
            if user:
                self.redirect('/playerform?error=' + unicode_urlencode(player.name) + ' ja existe na base de dados')
                
            else:
                player.put()
                memcache.delete_multi(['allplayers','allplayers_byname'])
                self.redirect('/gameform?playeradded=' + unicode_urlencode(player.name))


class PlayerList(webapp.RequestHandler):
  
    def get(self):
        players = from_cache_else_query('allplayers_byname')
        self.response.headers['Content-Type'] = 'text/javascript'
        jogadores = []
        for p in players:
            j = {
                'value': str(p.key()),
                'label':  p.name
            }
            jogadores.append(j)
        self.response.out.write("loadWorksheet("+json.dumps(jogadores)+")")


class AdminPage(webapp.RequestHandler):
    def get(self):
        menu = loginmenu(self.request.uri)
        games = from_cache_else_query('allgames')
        
        template_values = {
          'page_title' : 'Ranking -  liga de King',
          'page_header' : 'Ranking -  liga de King',
          'games' : games,
          'url' : menu[0],
          'url_linktext' : menu[1],
          'user' : menu[2],
          'admin' : users.is_current_user_admin(),
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/admin.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        selectedgames = self.request.get_all('gamecheck')
        action = self.request.get('submit')
        
        def regenerateTrueSkill():
            resetPlayerScores()
            trueskill.SetParameters(
                                trueskill_config.beta,
                                trueskill_config.epsilon,
                                trueskill_config.draw_probability, 
                                trueskill_config.gamma
                                )
            
            all_games = Game.all().order('dateplayed').fetch(1000)
            allplayers = from_cache_else_query('allplayers')
            
            for p in allplayers:
                p.encoded_key = str(p.key())
                        
            for game in all_games:
                # logging.debug(game.dateplayed)
                gameplayers = []
                for playerkey in game.player_keys:
                    for index,player in enumerate(allplayers):
                        if str(playerkey) == player.encoded_key:
                            gameplayers.append(allplayers.pop(index))

                for player, score in zip(gameplayers, game.scores):
                    player.games_played = player.games_played + 1
                    player.skill = (player.mu, player.sigma)
                    player.rank = score*-1
                    
                trueskill.AdjustPlayers(gameplayers)            
                
                for p in gameplayers:
                    p.previous_mu = p.mu
                    p.mu = p.skill[0]
                    p.previous_sigma = p.sigma
                    p.sigma = p.skill[1]
                    p.previous_skill = p.current_skill
                    p.current_skill = p.mu - trueskill_config.k*p.sigma
                    allplayers.insert(0, p)

                allplayers.sort(key=operator.attrgetter("current_skill"), reverse=True)
                for i, p in enumerate(allplayers):
                    if p.previous_rank == 0:
                        p.previous_rank = i + 1
                    else:
                        p.previous_rank = p.current_rank
                    p.current_rank = i + 1
            
            db.put(allplayers)
            memcache.delete_multi(['allgames','allplayers','allplayers_byname'])
            self.redirect('/')
            
        
        def deleteSelectedGames():            
            gameobjects = db.get(selectedgames)
            db.delete(gameobjects)
            regenerateTrueSkill()
            memcache.delete('allgames')
            self.redirect('/')
        
        def deleteAllGames():
            gameobjects = from_cache_else_query('allgames')
            if gameobjects:
                db.delete(gameobjects)
                memcache.delete('allgames')
            resetPlayerScores()
            self.redirect('/')
            
        def resetPlayerScores():    
            playerobjects = from_cache_else_query('allplayers')
            if playerobjects:
                for p in playerobjects:
                    p.games_played = 0
                    p.mu = trueskill_config.default_mu
                    p.previous_mu = trueskill_config.default_mu
                    p.sigma = trueskill_config.default_sigma
                    p.previous_sigma = trueskill_config.default_sigma
                    p.current_skill = 0.0
                    p.previous_skill = 0.0
                    p.current_rank = 0
                    p.previous_rank = 0
                db.put(playerobjects)
                memcache.delete_multi(['allgames','allplayers'])
            self.redirect('/')
            
        def deleteAllPlayers():
            gameobjects = from_cache_else_query('allgames')
            if gameobjects:
                db.delete(gameobjects)
            
            playerobjects = from_cache_else_query('allplayers')
            if playerobjects:
                db.delete(playerobjects)
            memcache.delete_multi(['allgames','allplayers','allplayers_byname'])
            self.redirect('/')
            
            
        if action == 'Delete selected Games':
            deleteSelectedGames()
        
        elif action == 'Delete ALL Games':
            deleteAllGames()
        
        elif action == 'Delete ALL Players':
            deleteAllPlayers()
        
        elif action == 'Reset Player Scores':
            resetPlayerScores()        
        
        elif action == 'Regenerate Rankings':
            regenerateTrueSkill()
            

# ==============================================================
# APP ROUTING and RUN:
# ==============================================================            
application = webapp.WSGIApplication([
                                    ('/', MainPage),
                                    ('/faq', FAQPage),
                                    ('/games', GamesPage),
                                    ('/games-rss.xml', GamesRSS),
                                    ('/gameform', GameFormPage),
                                    ('/playerform', PlayerFormPage),
                                    ('/newgame', PutGame),
                                    ('/newplayer', PutPlayer),
                                    ('/playerlist', PlayerList),
                                    ('/admin', AdminPage),
                                    ],debug=True)

                                    
def main():
    run_wsgi_app(application)

    
if __name__ == "__main__":
    main()