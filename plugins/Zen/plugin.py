
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from random import choice

class Zen(callbacks.Plugin):
    """Add the help for "@plugin help Zen" here
    This should describe *how* to use this plugin."""
    threaded = True

    proverbs = """
A samurai once asked Zen Master Hakuin where he would go after he died. Hakuin answered 'How am I supposed to know?' 'How do you not know? You're a Zen master!' exclaimed the samurai. 'Yes, but not a dead one,' Hakuin answered.
Do not seek the truth, only cease to cherish your opinions.
If you understand, things are just as they are; if you do not understand, things are just as they are.
In the landscape of spring, there is neither better nor worse. The flowering branches grow naturally, some long, some short.
Knock on the sky and listen to the sound.
The ten thousand questions are one question. If you cut through the one question, then the ten thousand questions disappear.
The ways to the One are as many as the lives of men.
Though the bamboo forest is dense, water flows through it freely.
To do a certain kind of thing, you have to be a certain kind of person.
To follow the path, look to the master, follow the master, walk with the master, see through the master, become the master.
When the pupil is ready to learn, a teacher will appear.
When you reach the top, keep climbing.
Why do you ask questions? If you already knew the flame was fire then the meal was cooked a long time ago. (Oma Desala, Stargate SG-1; various)
A river too pure, yields no fish.
At first, I saw mountains as mountains and rivers as rivers. Then, I saw mountains were not mountains and rivers were not rivers. Finally, I see mountains again as mountains, and rivers again as rivers.
No yesterday, no tomorrow, and no today - Sheng-ts'an
If the problem has a solution, worrying is pointless, in the end the problem will be solved. If the problem has no solution, there is
 no reason to worry, because it can't be solved.
Do not seek to follow in the footsteps of the men of old; seek what they sought. Basho
An autumn night... don't think your life, didn't matter. Basho
There is nothing you can see that is not a flower; there is nothing you can think that is not the moon. Basho
At any given moment, I open my eyes and exist. And before that, during all eternity, what was there? Nothing. Ugo Betti
The torch of doubt and chaos, this is what the sage steers by. Chuang-tzu
It is everywhere. Chuang-tzu
To a mind that is still, the whole universe surrenders. Chuang-tzu
If you cannot find the truth right where you are, where else do you expect to find it? Dogen
Zazen is itself enlightenment. Dogen
The whole moon and the entire sky are reflected in one dewdrop on the grass. Dogen
There is no beginning to practice nor end to enlightenment; There is no beginning to enlightenment nor end to practice. Dogen
And the end of all our exploring will be to arrive where we started and know the place for the first time. T.S. Eliot
When you are deluded and full of doubt, even a thousand books of scripture are not enough. When you have realized understanding, even one word is too much. Fen-Yang
Should you desire great tranquility, prepare to sweat white beads. Hakuin
Zen: Seeing into one's own nature. Hui-neng
How do you step from the top of a 100-foot pole? koan
It is better to practice a little than talk a lot. Muso Kokushi
We shape clay into a pot, but it is the emptiness inside that holds whatever we want. Lao Tzu
A journey of a thousand miles begins with a single step. Lao Tzu
So little time, so little to do. Oscar Levant
The only Zen you find on the tops of mountains is the Zen you bring up there. Robert M. Pirsig
The fundamental delusion of humanity is to suppose that I am here and you are out there. Yasutani Roshi
The quieter you become, the more you can hear. Baba Ram Dass
Natural and super-natural, temporal and eternal - continuums, not absolutes. Albert Schweitzer (paraphrased)
You must neither strive for truth nor seek to lose your illusions. The Shodoka
We have two eyes to see two sides of things, but there must be a third eye which will see everything at the same time and yet not see anything. That is to understand Zen. D. T. Suzuki
As long as you seek for something, you will get the shadow of reality and not reality itself. Shunryu Suzuki
Zen is not some kind of excitement, but merely concentration on our usual everyday routine. Shunkyu Suzuki
In the beginner's mind there are many possibilities, but in the expert's mind there are few. Shunryu Suzuki
The most important point is to accept yourself and stand on your two feet. Shunryu Suzuki
Life is like stepping onto a boat that is about to sail out to sea and sink. Shunryu Suzuki
My heart burns like fire but my eyes are as cold as dead ashes. Sayen Shaku
To set up what you like against what you don't like -- this is the disease of the mind. Sheng-ts'an
No yesterday, no tomorrow, and no today. Sheng-ts'an
Don't seek reality, just put an end to opinions. Sheng-ts'an
u"When you get there, there isn't any there there. Gertrude Stein
Water which is too pure has no fish. Ts'ai Ken T'an
Nothing is exactly as it seems, nor is it otherwise. Alan Watts
Let the dead bury the dead. Western Koan
What does mysticism mean? It means the way to attain knowledge. It's close to philosophy, except in philosophy you go horizontally while in mysticism you go vertically. Elie Wiesel
Ten thousand flowers in spring the moon in autumn, a cool breeze in summer, snow in winter. If your mind isn't clouded by unnecessary things, this is the best season of your life. Wu-men
Since it is all too clear It takes time to grasp it. When you understand that it's foolish to look for fire with fire, The meal is already cooked. Wu-men
The instant you speak about a thing, you miss the mark.
If you're attached to anything, you surely will go far astray.
Only the crystal-clear question yields a transparent answer.
All of the significant battles are waged within the self.
Life is the only thing worth living for.
Better to sit all night than to go to bed with a dragon.
Live every day like your hair was on fire.
If you understand, things are just as they are; if you do not understand, things are just as they are.
When you get to the top of the mountain, keep climbing.
The mind should be as a mirror. There is nothing infinite apart from finite things.
Everyday life is the way.
Great Faith. Great Doubt. Great Effort. - The three qualities necessary for training.
If you do not get it from yourself, Where will you go for it?
Do not permit the events of your daily life to bind you, but never withdraw yourself from them.
Where there is great doubt, there will be great awakening; small doubt, small awakening, no doubt, no awakening.
Sitting peacefully doing nothing Spring comes and the grass grows all by itself.
Everything the same; everything distinct.
Lovely snowflakes, they fall nowhere else!
Chop wood, carry water.
Possessing much knowledge is like having a thousand foot fishing line with a hook, but the fish is always an inch beyond the hook.
A noble heart never forces itself forward. Its words are as rare gems, seldom displayed and of great value.
If you meet on the way a man who knows, Don't speak a word -- Don't keep silent!
Even a good thing isn't as good as nothing.
This is not the Buddha, this is the Buddha.
One moon shows in every pool, in every pool the one moon.
Studying Zen, learning the way, is originally for the sake of birth and death, no other thing.
What do I mean by other things? Arousing the mind and stirring thoughts right now; having contrivance and artificiality; having grasping and rejecting; having practice and realization; having purity and defilement; having sacred and profane; having Buddhas and sentient beings; writing verses and songs, composing poems and odes; discoursing on Zen and the way; discoursing on right and wrong; discoursing on past and present.
These various activities are not relevant to the issue of birth and death; they are all "other things." Chien-ju
No ego, no pain.
The journey of a thousand miles must begin with a single step.
The world is like a mirror you see? smile and your friends smile back.
Your Treasure House is in yourself, it contains all you need.
He who asks a question is a fool for a minute; he who does not remains a fool forever.
The tongue like a sharp knife... Kills without drawing blood.
All that we are is the result of what we have thought. The mind is everything. What we think we become.
A jug fills drop by drop.
We cannot see our reflection in running water. It is only in still water that we can see.
One moon shows in every pool in every pool the one moon.
Student says " I am very discouraged. What should I do?" Master says, "encourage others."
A flower falls even though we love it and a weed grows even though we do not love it.
When the pupil is ready to learn, a teacher will appear.
It takes a wise man to learn from his mistakes, but an even wiser man to learn from others.
If you understand, things are just as they are; if you do not understand, things are just as they are.
When the character of a man is not clear to you, look at his friends.
Water and words... Easy to pour impossible to recover.
Teachers open the door... You enter by yourself.
A wise man makes his own decisions, an ignorant man follows the public opinion.
The rich man plans for tomorrow... The poor man for today.
To know the road ahead, ask those coming back.
The path of the enlightened one leaves no track- it is like the path of birds in the sky.
Before enlightenment: Chop wood, carry water. After enlightment: Chop wood, carry water.
Give a man a fish and you feed him for a day. Teach a man to fish and you feed him for a lifetime.
At birth we come At death we go... Bearing nothing.
One beam alone... No matter how stout... Cannot support a house.
No road to happiness or sorrow... Find them in yourself.
You will not be punished for your anger; you will be punished by your anger.
What is the path? the Zen Master Nan-sen was asked. Everyday life is the path, he answered.
Do not speak - unless it improves on silence.
If you light a lamp for somebody, it will also brighten your own path.
In criticizing, the teacher is hoping to teach. That's all.
Although gold dust is precious, when it gets in your eyes, it obstructs your vision.
We are shaped by our thoughts; we become what we think. When the mind is pure, joy follows like a shadow that never leaves.
    """

    def zen(self, irc, msg, args):
        """
        a random zen proverb from a list taken from http://en.wikiquote.org/wiki/Zen_proverbs
        """
        plist = [x for x in Zen.proverbs.split("\n") if len(x.strip())]
        p = choice(plist)
        irc.reply(p.strip(), prefixNick=False)

Class = Zen

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
