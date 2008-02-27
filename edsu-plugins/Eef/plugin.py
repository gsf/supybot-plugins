from supybot.commands import *
import supybot.callbacks as callbacks
import re
import random

class Eef(callbacks.Privmsg):

    def eef(self,irc,msg,args):
    	"""
	Get a random bit of wisdom from http://www.joke-archives.com/oneliners/if.html
	"""
    	irc.reply(quotes[random.randint(0,len(quotes))])

Class = Eef

quotes = \
"""
If a listener nods his head when you're explaining yourprogram, wake him up.
If a man advances confidently in the direction of his dreams tolive the life he has imagined, he will meet with a successunexpected in common hours. - Henry David Thoreau
If a program is useful it will be changed, if it is useless, itwill be documented.
If a straight line fit is required, obtain only two datapoints.
If all you have is a hammer, everything looks like a nail.
If an experiment works, you must be using the wrong equipment.
If an item is advertised as "under $50", you can bet it's not$19.95.
If anything can go wrong, it will.
If anything is used to its full potential, it will break.
If at first you do succeed, try to hide your astonishment.
If at first you don't succeed, blame it on your supervisor.
If at first you don't succeed, cheat!
If at first you don't succeed, destroy all evidence that youtried.
If at first you don't succeed, give up. No use being a damnfool.
If at first you don't succeed, redefine success.
If at first you don't succeed, skydiving is not your sport.
If at first you don't succeed, transform your dataset.
If at first you don't succeed, try something else.
If at first you don't succeed, well...darn.
If at first you don't succeed, you probably didn't really careanyway.
If at first you don't succeed, you'll get a lot of free advicefrom folks who didn't succeed either.
If at first you don't succeed, you're doing about average.
If at first you don't succeed, your successor will.
If builders built buildings the way programmers wrote programs,then the first woodpecker that came along would destroycivilization.
If enough data is collected, anything can be proven bystatistical methods.
If everything is coming your way, you are probably in the wronglane.
If everything seems to be going well, you obviously do not knowwhat is going on.
If everything seems to go right, check your zipper.
If facts do not conform to the theory, they must be disposedof.
If flattery gets you nowhere, try bribery.
If I want your opinion, I'll ask you to fill out the necessaryform.
If ignorance is bliss, why aren't there more happy people?
If ignorance is bliss, most of us must be orgasmic.
If it can be borrowed and it can be broken, you will borrow itand you will break it.
If it doesn't make sense, it's either economics or psychology.
If it doesn't work, expand it.
If it happens, it must be possible.
If it is good, they will stop making it.
If it is incomprehensible, it's mathematics.
If it is worth doing, it is worth doing for money.
If it is worth doing, it is worth over-doing.
If it jams, force it. If it breaks, it needed replacing anyway.
If it looks too good to be true, it is too good to be true.
If it says "one size fits all," it doesn't fit anyone.
If it weren't for the last minute, nothing would ever get done.
If it works, don't fix it!
If jackasses could fly, this place would be an airport.
If more than one person is responsible for a miscalculation, noone will be at fault.
If Murphy's Law can go wrong, it will.
If not controlled, work will flow to the competent man until hesubmerges.
If on an actuarial basis there is a 50-50 chance that somethingwill go wrong, it will actually go wrong nine times out of ten.
If only one price can be obtained for a quotation, the pricewill be unreasonable.
If opportunity came disguised as temptation, one knock would beenough.
If people listened to themselves more often, they would talkless.
If reproducibility might be a problem, conduct the test onlyonce.
If some people didn't tell you, you'd never know they'd beenaway on vacation.
If something is confidential, it will be left in the photocopymachine.
If something is done wrong often enough, it becomes right.
If 'success' consisted simply of not taking chances, then'glory' would be at the disposal of the most mediocre talent.
If the assumptions are wrong, the conclusions are not likely tobe very good.
If the code and the comments disagree, then both are probablywrong.
If the probability of success is not almost one, it is damnnear zero.
If the slightest probability for an unpleasant event to happenexists, the event will take place, preferably during ademonstration.
If there is a possibility of several things going wrong, theone that will cause the most damage will be the one to gowrong.
If there isn't a law, there will be.
If there is light at the end of the tunnel...order more tunnel.
If things were left to chance, they would be better.
If two wrongs don't make a right, try three.
If we learn by our mistakes, some of us are getting one hell ofan education!
If you aim for the stars but only make it to the moon, rememberthere are people who have not yet made it to the moon.
If you are already in a hole, there is no use to continuedigging.
If you are asked to join a parade, don't march behind theelephants.
If you are coasting, you're going downhill.
If you are feeling good, don't worry. You'll get over it.
If you are given two contradictory orders, obey them both.
If you are not the lead dog, the scenery never changes.
If you are running for a short line, it suddenly becomes a longline.
If you are worried about being crazy, don't be overlyconcerned. If you were, you would think you were sane.
If you can smile when things go wrong, you must have someone toblame.
If you cannot convince them, confuse them. - Harry S. Truman
If you cannot dazzle them with brilliance, baffle them withbullshit.
If you cannot fix it, feature it.
If you cannot get your work done in a 24-hour day, then worknights!
If you cannot measure output, then you measure input.
If you cannot hope for order, withdraw with style from thechaos.
If you consult enough experts, you can confirm any opinion.
If you did what you always did, you'll get what you always got.
If you do a job too well, you will get stuck with it.
If you do something right once, someone will ask you to do itagain.
If you do not care where you are, then you aren't lost.
If you do not change direction, you are likely to end up whereyou are headed.
If you do not know what you're doing, do it neatly.
If you do not like the answer, you shouldn't have asked thequestion.
If you do not make dust, you eat dust.
If you do not say it, they can't repeat it.
If you do not understand it, it must be intuitively obvious.
If you explain so clearly that no one can possiblymisunderstand, someone will.
If you file it, you'll know where it is but never need it. Ifyou don't file it, you'll need it but never know where it is.
If you have always done it that way, it is probably wrong.
If you have got them by the testicles, their hearts and mindswill follow.
If you have nothing to do, don't do it here.
If you have something to do, and you put it off long enough,chances are someone else will do it for you.
If you have to ask, you are not entitled to know.
If you just try long enough and hard enough, you can alwaysmanage to boot yourself in the posterior.
If you keep anything long enough, you can throw it away.
If you keep saying things are going to be bad, you have achance of being a prophet.
If you live in a country run by committee, be on the committee.
If you make people think they're thinking, they'll love you;but if you really make them think they'll hate you.
If you mess with a thing long enough, it will break.
If you plan to leave your mark in the sands of time, you betterwear work shoes.
If you put it off long enough, it might go away.
If you see a man approaching you with the obvious intent ofdoing you good, you should run for your life.
If you see that there are four possible ways in which aprocedure can go wrong, and circumvent these, then a fifth way,unprepared for, promptly develops.
If you stand in one place long enough, you make a line.
If you step out of a short line for a second, it becomes a longline.
If you think that OSHA is a small town in Wisconsin, you're introuble.
If you think the problem is bad now, just wait until we'vesolved it.
If you throw something away, you will need it the next day.
If you try to please everybody, nobody will like it.
If you understand it, it is obsolete.
""".split("\n")
