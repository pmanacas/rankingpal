"""
    Set global parameters used in the TrueSkill algorithm.

    beta is a measure of how random the game is.  You can think of it as
    the difference in skill (mean) needed for the better player to have
    an ~80% chance of winning.  A high value means the game is more
    random (I need to be *much* better than you to consistently overcome
    the randomness of the game and beat you 80% of the time); a low
    value is less random (a slight edge in skill is enough to win
    consistently).  The default value of beta is half of INITIAL_SIGMA
    (the value suggested by the Herbrich et al. paper).

    epsilon is a measure of how common draws are.  Instead of specifying
    epsilon directly you can pass draw_probability instead (a number
    from 0 to 1, saying what fraction of games end in draws), and
    epsilon will be determined from that.  The default epsilon
    corresponds to a draw probability of 0.1 (10%).  (You should pass a
    value for either epsilon or draw_probability, not both.)

    gamma is a small amount by which a player's uncertainty (sigma) is
    increased prior to the start of each game.  This allows us to
    account for skills that vary over time; the effect of old games
    on the estimate will slowly disappear unless reinforced by evidence
    from new games.
    
    k is the multiplier for the uncertainty when calculating the Conservative skill estimate (mu-k*sigma)
    a good default value for k is 3. which gives Conservative skill estimate = mu -3*sigma
    """

default_mu      = 25.0
default_sigma   = default_mu/3

beta             = 7
epsilon          = None
draw_probability = 0.0366666666666667
gamma            = 0.015
k                  = 3

# beta             = None
# epsilon          = None
# draw_probability = None
# gamma            = 0
# k                = 3